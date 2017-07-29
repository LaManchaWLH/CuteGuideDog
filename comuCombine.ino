#include <MsTimer2.h>
#include <math.h>
#include <Wire.h>
#include <LSM303.h>
#include <NewPing.h>

#define HELLO 0x12
#define ACK 0x11
#define WORKING 0x13
#define ERROR1 0x14
#define ARRIVE 0x18
#define RCV 0x20
#define NORTH 0x23

#define BYTE0(dwTemp)       ( *( (char *)(&dwTemp)    ) )
#define BYTE1(dwTemp)       ( *( (char *)(&dwTemp) + 1) )
#define BYTE2(dwTemp)       ( *( (char *)(&dwTemp) + 2) )
#define BYTE3(dwTemp)       ( *( (char *)(&dwTemp) + 3) )

#define AutoCalibrateEn 1

#define Stop 0
#define Line 1
#define Turn 2
#define TurnComp 3

/****** Pin define *******/
#define leftDir 4
#define rightDir 7
#define leftWid 5
#define rightWid 6
#define codeLeft 2
#define codeRight 3
#define trigger0  41  
#define echo0     40  
#define trigger1  46  
#define echo1     47  
#define trigger2  48  
#define echo2     49  
/****** Parameter define ******/
//pid for position
#define IlenPos 8
#define kpPos 0.22
#define kiPos 0.00001
#define kdPos 0.02
//#define kpDir 0.05
//#define kiDir 0.02/IlenPos
#define IMaxPos 4
//#define IMaxDir 7

//for speed loop
#define kpSpd 2
#define kiSpd 0.000036
#define kdSpd 0.35
#define IlenSpd 20
#define IMaxSpd 50
#define timeGap 25//ms

//for line calibrate
#define kpLine 0.083//28
#define kiLine 0//.000045
#define kdLine 0.015
#define IlenLine 20
#define IMaxLine 4
#define lineMax 7

//maximun constrain value
#define pwmMax 250//the maximun of pwm output
#define speedMax 2//the maximun of speed loop input(need change by timeGap)

#define m1 1885
#define dm1 188
#define cm1 18.85
#define trn90 213
#define turnSpeed 1
#define angJudge 30
#define turnJudge 6
#define posiJudge 10

#define MAX_DISTANCE 200

/****** Class define ******/
class PidItgData{
  private:
  int* data;
  int dataNum;
  public:
  PidItgData(int num)
  {
    data = new int[num]();
    dataNum = num;
  };
  void InsertData(int newData)
  {
    for (int i = dataNum-1;i>0;i--)
      data[i] = data[i-1];
    data[0] = newData;
  }
  int Sum(void)
  {
    int sum = 0;
    for (int i = 0; i<dataNum;i++)
      sum += data[i];
    return sum;
  }
  int Old(void){
    return data[1];
  }
  void Clear(){
    for(int i = 0;i<dataNum;i++){
      data[i] = 0;
    }
    return;
  }
};

/****** Global Variables define ******/
volatile bool stopFlag = 1;
volatile bool turnFlag = 0;
volatile int workState = 0;
//for position loop
volatile long codeCntLeft=0,codeCntRight=0;//encoder valu counter
volatile long aimCntLeft=0,aimCntRight=0;//aim valu
//PidItgData posiPidItg(IlenPos);//for I 

//for speed loop
volatile int leftCurSpeed=0,rightCurSpeed=0;
volatile int t_leftAimSpeed=0,t_rightAimSpeed=0;//for test
volatile int pwmValLeft=0,pwmValRight=0;//pwm output
int codeCntLeftOld=0,codeCntRightOld=0;
PidItgData leftSpeedPidItg(IlenSpd), rightSpeedPidItg(IlenSpd);//for I

//for line calibrate
int posiDif=0;
PidItgData linePidItg(IlenLine);

//for direction
LSM303 compass;
LSM303::vector<int16_t> running_min = {32767, 32767, 32767}, running_max = {-32768, -32768, -32768};

volatile int heading;
volatile int aimAngle=0;
//PidItgData dirPidItg(IlenPos);
PidItgData leftPosiPidItg(IlenPos), rightPosiPidItg(IlenPos);

//for print
long timeTick=0;

//for sonar
NewPing sonar0(trigger0, echo0, MAX_DISTANCE);
NewPing sonar1(trigger1, echo1, MAX_DISTANCE);
NewPing sonar2(trigger2, echo2, MAX_DISTANCE);
int sonar0Data = 0;
int sonar1Data = 0;
int sonar2Data = 0;

//for communication
volatile int connectSet = 0;
int aim[3]={};


/****** Code ******/
void setup()
{
  //serial init
  Serial.begin(115200);
  Serial1.begin(9600);
  //pin init
  pinMode(leftDir, OUTPUT);
  pinMode(rightDir, OUTPUT);
  pinMode(leftWid, OUTPUT);
  pinMode(rightWid, OUTPUT);
  pinMode(codeLeft, INPUT_PULLUP);
  pinMode(codeRight, INPUT_PULLUP);
  pinMode(13,OUTPUT);
  //interrup init
  attachInterrupt(digitalPinToInterrupt(codeLeft), LeftCodeUpdate, CHANGE);
  attachInterrupt(digitalPinToInterrupt(codeRight), RightCodeUpdate, CHANGE);

  Wire.begin();
  MsTimer2::set(timeGap, SpeedUpdate);
  MsTimer2::start();
  compass.init();
  compass.enableDefault();
  if(AutoCalibrateEn == 0){
    compass.m_min = { -3083,  -3802,   -948};
    compass.m_max = { +1159,   +989,  +2816};
  }
  else{
    CompassCalibrate();
    compass.m_min = (LSM303::vector<int16_t>){ running_min.x, running_min.y, running_min.z};
    compass.m_max = (LSM303::vector<int16_t>){ running_max.x, running_max.y, running_max.z};
  }
}

void CompassCalibrate(){
  int i;
  stopFlag = 0;
  Serial1.println("Start Calibrate!");
  digitalWrite(leftDir, 1);
  digitalWrite(rightDir, 0);
  analogWrite(leftWid, 250);
  analogWrite(rightWid, 250);
  for(i=0;i<500;i++){
    compass.read();
    running_min.x = min(running_min.x, compass.m.x);
    running_min.y = min(running_min.y, compass.m.y);
    running_min.z = min(running_min.z, compass.m.z);
    running_max.x = max(running_max.x, compass.m.x);
    running_max.y = max(running_max.y, compass.m.y);
    running_max.z = max(running_max.z, compass.m.z);
    delay(10);
  }
  digitalWrite(leftDir, 0);
  digitalWrite(rightDir, 1);
  analogWrite(leftWid, 250);
  analogWrite(rightWid, 250);
  for(i=0;i<500;i++){
    compass.read();
    running_min.x = min(running_min.x, compass.m.x);
    running_min.y = min(running_min.y, compass.m.y);
    running_min.z = min(running_min.z, compass.m.z);
    running_max.x = max(running_max.x, compass.m.x);
    running_max.y = max(running_max.y, compass.m.y);
    running_max.z = max(running_max.z, compass.m.z);
    delay(10);
  }
  digitalWrite(leftDir, 1);
  digitalWrite(rightDir, 1);
  analogWrite(leftWid, 0);
  analogWrite(rightWid, 0);
  stopFlag = 1;
  Serial1.println("Calibrate Completed!");
}

/******interrupt function******/
void LeftCodeUpdate(){//interrupt 0
  if(pwmValLeft>0) codeCntLeft++;
  else codeCntLeft--;
  //codeCntLeft++;
}

void RightCodeUpdate(){//interrupt 1
  if(pwmValRight>0) codeCntRight++;
  else codeCntRight--;
  //codeCntRight++;
}

void serialEvent1(){
  char a = Serial1.read(); 
  //Serial1.println(a);
  if(a == 'w') {
    aimCntLeft = codeCntLeft + m1;
    aimCntRight = codeCntRight + dm1;
    t_leftAimSpeed  += 2;
    t_rightAimSpeed += 2;
    posiDif = codeCntLeft - codeCntRight;
    linePidItg.Clear();
    workState = Line;
    stopFlag = 0;//start
  }
  else if(a == 's'){
    aimCntLeft = codeCntLeft - m1;
    aimCntRight = codeCntRight - dm1;
    t_leftAimSpeed  -= 2;
    t_rightAimSpeed -= 2;
    aimAngle = heading;
    posiDif = codeCntLeft - codeCntRight;
    linePidItg.Clear();
    workState = Line;
    stopFlag = 0;//start
  }
  else if(a == 'a'){
    aimCntLeft  = codeCntLeft - trn90;
    aimCntRight = codeCntRight + trn90;
    leftPosiPidItg.Clear();
    rightPosiPidItg.Clear();
    leftSpeedPidItg.Clear();
    rightSpeedPidItg.Clear();
    //aimAngle = ((heading - 900)+3600)%3600;
    workState = Turn;
    stopFlag = 0;//start
  }
  else if(a == 'd'){
    aimCntLeft  = codeCntLeft + trn90;
    aimCntRight = codeCntRight - trn90;
    leftPosiPidItg.Clear();
    rightPosiPidItg.Clear();
    leftSpeedPidItg.Clear();
    rightSpeedPidItg.Clear();
    //aimAngle = ((heading + 900)+3600)%3600;
    workState = Turn;
    stopFlag = 0;//start
  } 
  else if(a == 'n'){
    aimAngle = 1800;
    workState = TurnComp;
    stopFlag = 0;//start
  }
  else if(a == 'b'){
    aimAngle = 0;
    workState = TurnComp;
    stopFlag = 0;//start
  }
  else if(a == 'z'){
    codeCntLeft  = 0;
    codeCntRight = 0;
    aimCntLeft  = codeCntLeft;
    aimCntRight = codeCntRight;
    t_leftAimSpeed = 0;
    t_rightAimSpeed = 0;
    stopFlag = 1;
    workState = Stop;
    connectSet = 0;
  }
  else if(a == 'x'){
    stopFlag = 1;
    workState = Stop;
    t_leftAimSpeed = 0;
    t_rightAimSpeed = 0;
  }
}

/******main function*******/
void loop()
{ 
  int errL,errR;
  SenserUpdate();

  if(ReceiveData() == 0){//aim data available
    if(aim[0] != 0){
      turnFlag = 0;
      stopFlag = 0;
      workState = Line;
      aimCntLeft = codeCntLeft + aim[0]*cm1;
      aimCntRight = codeCntRight + aim[0]*cm1;
      posiDif = codeCntLeft - codeCntRight;
      Serial1.println("RCV:Line");
    }
    else if(aim[1] != 0){
      turnFlag = 1;
      stopFlag = 0;
      workState = Turn;
      aimCntLeft = int(float(codeCntLeft) + float(aim[1])*trn90/90);
      aimCntRight = int(float(codeCntRight) - float(aim[1])*trn90/90);
      Serial1.println("RCV:Turn");
    }
    else if(aim[2] != 0){
      turnFlag = 1;
      stopFlag = 0;
      aimAngle = aim[2]-1;
      aim[2] = 0;
      workState = TurnComp;
      Serial1.println("RCV: TurnComp");
    }
    SendData(RCV);
  }
  
  switch(workState){
    case Stop:
      stopFlag = 1;
      digitalWrite(leftDir, 1);
      digitalWrite(rightDir, 1);
      analogWrite(leftWid, 0);
      analogWrite(rightWid, 0);
      aimCntLeft = codeCntLeft;
      aimCntRight = codeCntRight;
      leftPosiPidItg.Clear();
      rightPosiPidItg.Clear();
      leftSpeedPidItg.Clear();
      rightSpeedPidItg.Clear();
      linePidItg.Clear();
      pwmValLeft      = 0;
      pwmValRight     = 0;
      break;
    case Line:
      //SetSpeedLine(t_leftAimSpeed);
      
      SetPositionLine(aimCntLeft,9);
      errL = abs(aimCntLeft-codeCntLeft);
      if(errL<posiJudge){
        stopFlag = 1;
        workState = Stop;
        //aimCntLeft = codeCntLeft;
        //aimCntRight = codeCntRight;
        leftPosiPidItg.Clear();
        rightPosiPidItg.Clear();
        leftSpeedPidItg.Clear();
        rightSpeedPidItg.Clear();
        linePidItg.Clear();
        pwmValLeft      = 0;
        pwmValRight     = 0;
        SendData(ARRIVE);
        Serial1.println("ARRIVE:Line");
      }
      break;
    case Turn:
      SetPositionTurn(aimCntLeft,aimCntRight,speedMax);
      errL = abs(aimCntLeft-codeCntLeft);
      errR = abs(aimCntRight-codeCntRight);
      if(errL<turnJudge&&errR<turnJudge){
        stopFlag = 1;
        workState = Stop;
        aimCntLeft = codeCntLeft;
        aimCntRight = codeCntRight;
        leftPosiPidItg.Clear();
        rightPosiPidItg.Clear();
        leftSpeedPidItg.Clear();
        rightSpeedPidItg.Clear();
        linePidItg.Clear();
        pwmValLeft      = 0;
        pwmValRight     = 0;
        SendData(ARRIVE);
        Serial1.println("ARRIVE:Turn");
      }
      break;
    case TurnComp:
      if(SetDirection(aimAngle) == 0){
        workState = Stop;
        leftPosiPidItg.Clear();
        rightPosiPidItg.Clear();
        leftSpeedPidItg.Clear();
        rightSpeedPidItg.Clear();
        pwmValLeft      = 0;
        pwmValRight     = 0;
        SendData(ARRIVE);
        Serial1.println("ARRIVE:TurnComp");
      }
      break;
    default:
      stopFlag = 1;
    break;
  }

  if(timeTick<millis()){
    if(connectSet == 1){
      //SendData(WORKING);
    }
    else{
      SendData(HELLO);
    }
    timeTick = millis()+500;
    Serial1.print("H:");
    Serial1.print(heading);
    Serial1.print("  ");
    Serial1.print(posiDif);
    Serial1.print("  ");
    Serial1.print(codeCntLeft - codeCntRight);
    Serial1.print("  ");
    Serial1.print(aimCntLeft - aimCntRight);
    //Serial1.print(codeCntRight);
    Serial1.print(" LD:");
    Serial1.print(int(codeCntLeft));///18.85));
    Serial1.print("cm RD:");
    Serial1.print(int(codeCntRight));///18.85));
    Serial1.print("cm ");
    //Serial1.print("S0:");
    //Serial1.print(pwmValLeft);
    //Serial1.print("  ");
    //Serial1.print(pwmValRight);
    //Serial1.println("");
    //Serial1.print("Ping: ");
    //Serial1.print(sonar0Data); // Send ping, get distance in cm and print result (0 = outside set distance range)
    //Serial1.print("cm S1:");
    //Serial1.print(sonar1Data);
    //Serial1.print("cm S2:");
    //Serial1.print(sonar2Data);
    //Serial1.print("cm");
    Serial1.print(" Sp: ");
    Serial1.print(t_leftAimSpeed);
    Serial1.print("  ");
    Serial1.print(t_rightAimSpeed);
    Serial1.print("  ");
    Serial1.print(leftCurSpeed);
    Serial1.print("  ");
    Serial1.print(rightCurSpeed);
    Serial1.print(" aim: ");
    Serial1.print(aim[0]);
    Serial1.print(" ");
    Serial1.print(aim[1]);
    Serial1.print(" ");
    Serial1.print(connectSet);
    Serial1.print(" pos: ");
    Serial1.print(aimCntLeft);
    Serial1.print(" ");
    Serial1.print(aimCntRight);
    Serial1.print(" work:");
    Serial1.print(workState);
    Serial1.println("");
  }
}

void SenserUpdate(){
  compass.read();
  heading = int(compass.heading()*10);//0 is north
  sonar0Data = sonar0.ping_cm();
  sonar1Data = sonar1.ping_cm();
  sonar2Data = sonar2.ping_cm();
}

void SpeedUpdate(){//update speed
  leftCurSpeed    = (codeCntLeft - codeCntLeftOld);
  rightCurSpeed   = (codeCntRight - codeCntRightOld);
  codeCntLeftOld  = codeCntLeft;//update old data
  codeCntRightOld = codeCntRight;
  //digitalWrite(13, codeCntLeft % 2);
}

void SetSpeed(int leftAimSpeed,int rightAimSpeed){//input aim speed
  if(leftAimSpeed>0) leftAimSpeed++;
  else leftAimSpeed--;
  if(rightAimSpeed>0) rightAimSpeed++;
  else rightAimSpeed--;
  if(leftAimSpeed<=1&&leftAimSpeed>=-1) leftAimSpeed = 0;
  if(rightAimSpeed<=1&&rightAimSpeed>=-1) rightAimSpeed = 0;//consider 1 as 0;
  
  pwmValLeft  += SpeedPidCal(leftCurSpeed, leftAimSpeed, leftSpeedPidItg);
  pwmValRight += SpeedPidCal(rightCurSpeed, rightAimSpeed, rightSpeedPidItg);
  pwmValLeft  = constrain(pwmValLeft, -pwmMax, pwmMax);
  pwmValRight = constrain(pwmValRight, -pwmMax, pwmMax);

  if(stopFlag == 1){
    pwmValLeft      = 0;
    pwmValRight     = 0;
    t_leftAimSpeed  = 0;
    t_rightAimSpeed = 0;
  }

  digitalWrite(leftDir, (pwmValLeft>0) );
  digitalWrite(rightDir, (pwmValRight>0) );
  analogWrite(leftWid, abs(pwmValLeft) );
  analogWrite(rightWid, abs(pwmValRight) );
  return;
}

void SetSpeedLine(int aimSpeed){
  int posiErr = posiDif - (codeCntLeft - codeCntRight);
  linePidItg.InsertData(posiErr);
  int pidP = int(posiErr*kpLine);
  int pidI = int(linePidItg.Sum()*kiLine);
  int pidD = int(kdLine*(aimSpeed - linePidItg.Old()));
  pidI = constrain(pidI, -IMaxLine, IMaxLine);
  SetSpeed(aimSpeed+constrain(pidP+pidI, -lineMax, lineMax)
    , aimSpeed+constrain(-pidP-pidI, -lineMax, lineMax));
  return;
}

int SetDirection(int angle){
  int angErr = heading - angle;
  int dirFlag = 1;//1:left -1:right
  if(angErr < 0){
    dirFlag = -dirFlag;
    angErr = -angErr;
  }
  if(angErr > 1800){
    dirFlag = -dirFlag;
    angErr = 3600 - angErr;
  }

  SetSpeed(-dirFlag*turnSpeed,dirFlag*turnSpeed);
  if(abs(angErr)<angJudge) {
    turnFlag = 0;
    stopFlag = 1;
    return 0;
  }
  return 1;
}

void SetPositionTurn(int leftAimPosi, int rightAimPosi, int spdMax){
  int leftAimSpeed,rightAimSpeed;
  leftAimSpeed  = PositionPidCal(codeCntLeft, leftAimPosi, leftPosiPidItg);
  rightAimSpeed = PositionPidCal(codeCntRight, rightAimPosi, rightPosiPidItg);
  SetSpeed(constrain(leftAimSpeed, -spdMax, spdMax), constrain(rightAimSpeed,-spdMax,spdMax));
  return;
}

void SetPositionLine(int aimPosi, int spdMax){
  int aimSpeed;
  aimSpeed = PositionPidCal(codeCntLeft, aimPosi, leftPosiPidItg);
  SetSpeedLine(constrain(aimSpeed, -spdMax, spdMax));
  return;
}

int SpeedPidCal(int curSpeed, int aimSpeed, PidItgData &itgData){
  int speedErr = aimSpeed - curSpeed, pidOutPut;
  int pidP=0, pidI=0 , pidD=0;
  itgData.InsertData(speedErr);
  pidP = int(speedErr*kpSpd);
  pidI = int(itgData.Sum()*kiSpd);
  pidD = int(kdSpd*(speedErr - itgData.Old()));
  return pidP + constrain(pidI, -IMaxSpd, IMaxSpd) + pidD;
}

int PositionPidCal(long curPosi, long aimPosi, PidItgData &itgData){
  int posiErr = aimPosi - curPosi, pidOutPut;
  int pidP=0, pidI=0, pidD=0;
  itgData.InsertData(posiErr);
  pidP = int(posiErr*kpPos);
  pidI = int(itgData.Sum()*kiPos);
  pidD = int(kdPos*(posiErr - itgData.Old()));
  return pidP + constrain(pidI, -IMaxPos, IMaxPos) + pidD;
}

void SendData(char state){
  unsigned char sum = 0xA5;
  Serial.write(0xA5);
  if(connectSet == 0){
    state = HELLO;
  }
  Serial.write(char(state));
  if(state == WORKING){
    Serial.write(char(leftCurSpeed));
    Serial.write(char(rightCurSpeed));
    Serial.write(char(heading/20));
    Serial.write(BYTE3(codeCntLeft));
    Serial.write(BYTE2(codeCntLeft));
    Serial.write(BYTE1(codeCntLeft));
    Serial.write(BYTE0(codeCntLeft));
    Serial.write(BYTE3(codeCntRight));
    Serial.write(BYTE2(codeCntRight));
    Serial.write(BYTE1(codeCntRight));
    Serial.write(BYTE0(codeCntRight));
    Serial.write(BYTE0(sonar0Data));
    Serial.write(BYTE0(sonar1Data));
    Serial.write(BYTE0(sonar2Data));
    //if(speed% 5== 0) sum++;
    sum += BYTE0(sonar2Data);
    Serial.write(sum);
  }
  else{
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    Serial.write(0x01);
    sum += 0x01;
    Serial.write(sum);
  }
}


int ReceiveData(){
  unsigned char c,cc;
  int aimDisBufH,aimDisBufL,aimTurnBuf;
  while(1){
    if(Serial.read() == 0xFE) break;
    if(Serial.available() == 0) return 1;
  }
  //Serial1.write(0xFE);
  c = Serial.read();
  //Serial1.write(c);
  switch (c) {
      case ACK: 
        connectSet = 1;
        c = Serial.read();
        //Serial1.write(c);
        c = Serial.read();
        //Serial1.write(c);
        c = Serial.read();
        //Serial1.write(c);
        c += 0xFE;
        cc = Serial.read();
        //Serial1.write(cc);
        if(cc != c) {
          connectSet = 0;
          Serial1.write(c);
          Serial1.println("ACK Fail");
        }
        Serial1.println("ACK");
        delay(10);
        SendData(ACK);
        return 2;

      case WORKING: 
        c = Serial.read();
        //Serial1.write(c);
        aimDisBufH = c;
        c = Serial.read();
        //Serial1.write(c);
        aimDisBufL = c;
        c = Serial.read();
        //Serial1.write(c);
        aimTurnBuf = (int(c)-90)*2;
        c += 0xFE;
        cc = Serial.read();
        if(c == cc){
          BYTE1(aim[0]) = aimDisBufH;
          BYTE0(aim[0]) = aimDisBufL;
          aim[1] = aimTurnBuf;
          connectSet = 1;
        }
        //else connectSet = 0;
        //Serial1.write(cc);
        //Serial1.println("");
        return 0;
      case NORTH: 
        c = Serial.read();
        c = Serial.read();
        c = Serial.read();
        c = Serial.read();
        aim[2] = 1;
        return 0;
        
      default:
        //connectSet = 0;
        return 3;
  }
  return 0;
}

