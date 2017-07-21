#include <MsTimer2.h>
#include <math.h>
#include <Wire.h>
#include <LSM303.h>
#include <NewPing.h>
/****** Pin define *******/
#define leftDir 4
#define rightDir 7
#define leftWid 5
#define rightWid 6
#define codeLeft 2
#define codeRight 3
#define trigger0  12  
#define echo0     11  
#define trigger1  46  
#define echo1     47  
#define trigger2  48  
#define echo2     49  
/****** Parameter define ******/
//pid for position
#define IlenPos 10
#define kpPos 0.08
#define kiPos 0
#//define kpDir 0.05
//#define kiDir 0.02/IlenPos
#define kdPos 0
#define IMaxPos 50
//#define IMaxDir 7

//for speed loop
#define kpSpd 1.5
#define kiSpd 0
#define kdSpd 0
#define IlenSpd 10
#define IMaxSpd 80
#define timeGap 15//ms
//#define speedFixPar 50

//maximun constrain value
#define pwmMax 250//the maximun of pwm output
#define speedMax 6//the maximun of speed loop input(need change by timeGap)

#define m1 1885
#define dm1 188
#define trn90 200
#define turnSpeed 1
#define angJudge 50

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
    for (int i = dataNum;i>0;i--)
      data[i] = data[i-1];
    data[0] = newData;
  }
  int Sum(void)
  {
    int sum = 0;
    for (int i = 0; i<dataNum;i++)
      sum += data[i];
    return constrain(sum, -IMaxSpd, IMaxSpd);
  }
};

/****** Global Variables define ******/
volatile bool stopFlag = 0;
volatile bool turnFlag = 1;
//for position loop
volatile long codeCntLeft=0,codeCntRight=0;//encoder valu counter
volatile long aimCntLeft=0,aimCntRight=0;//aim valu
PidItgData posiPidItg(IlenPos);//for I 

//for speed loop
volatile int leftCurSpeed=0,rightCurSpeed=0;
volatile int t_leftAimSpeed=0,t_rightAimSpeed=0;//for test
volatile int pwmValLeft=0,pwmValRight=0;//pwm output
int codeCntLeftOld=0,codeCntRightOld=0;
PidItgData leftSpeedPidItg(IlenSpd), rightSpeedPidItg(IlenSpd);//for I

//for direction
LSM303 compass;
volatile int heading;
volatile int aimAngle=0;
//PidItgData dirPidItg(IlenPos);

//for print
long timeTick=0;

NewPing sonar0(trigger0, echo0, MAX_DISTANCE);
NewPing sonar1(trigger1, echo1, MAX_DISTANCE);
NewPing sonar2(trigger2, echo2, MAX_DISTANCE);

/****** Code ******/
void setup()
{
	//serial init
	Serial.begin(9600);
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
  compass.init();
  compass.enableDefault();
  compass.m_min = (LSM303::vector<int16_t>){ -1854,  -2918,   -259} ;
  compass.m_max = (LSM303::vector<int16_t>){ +1874,   +764,  +3948};
  MsTimer2::set(timeGap, SpeedUpdate);
  MsTimer2::start();
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
  	stopFlag = 0;//start
    turnFlag = 0;//dont turn
  	//aimCntLeft = codeCntLeft + dm1;
  	//aimCntRight = codeCntRight + dm1;
    t_leftAimSpeed  += 1;
    t_rightAimSpeed += 1;
  }
  else if(a == 's'){
   	stopFlag = 0;//start
    turnFlag = 0;//dont turn
    //aimCntLeft = codeCntLeft - dm1;
    //aimCntRight = codeCntRight - dm1;
    t_leftAimSpeed  -= 1;
    t_rightAimSpeed -= 1;
  }
  else if(a == 'a'){
    stopFlag = 0;//start
    turnFlag = 1;
    aimAngle = heading - 900;
  }
  else if(a == 'd'){
  	stopFlag = 0;//start
  	turnFlag = 1;
    aimAngle = heading + 900;
  }
  else if(a == 'n'){
    stopFlag = 0;//start
    turnFlag = 1;
    aimAngle = 1800;
  }
  else if(a == 'b'){
    stopFlag = 0;//start
    turnFlag = 1;
    aimAngle = 0;
  }
  else if(a == 'x'){
  	stopFlag = 1;
  }
}

/******main function*******/
void loop()
{ 
  compass.read();
  heading = int(compass.heading()*10);//0 is north

  if(turnFlag == 0) SetSpeed(t_leftAimSpeed,t_rightAimSpeed);
  else SetDirection(aimAngle);
  if(timeTick<millis()){
    timeTick = millis()+500;
    Serial1.print("H:");
    Serial1.print(compass.heading());
    //Serial1.print("  ");
    //Serial1.print(codeCntRight);
    Serial1.print(" LD:");
    //Serial1.print("Sp: ");
    //Serial1.print(t_leftAimSpeed);
    //Serial1.print("  ");
    //Serial1.print(t_leftAimSpeed);
    //Serial1.print("  ");
    Serial1.print(int(codeCntLeft/18.85));
    Serial1.print("cm RD:");
    Serial1.print(int(codeCntLeft/18.85));
    Serial1.print("cm S0:");
    //Serial1.print(pwmValLeft);
    //Serial1.print("  ");
    //Serial1.print(pwmValRight);
    //Serial1.println("");
    //Serial1.print("Ping: ");
    Serial1.print(sonar0.ping_cm()); // Send ping, get distance in cm and print result (0 = outside set distance range)
    Serial1.print("cm S1:");
    Serial1.print(sonar1.ping_cm());
    Serial1.print("cm S2:");
    Serial1.print(sonar2.ping_cm());
    Serial1.println("cm");
  }
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

  if(stopFlag){
    pwmValLeft  = 0;
    pwmValRight = 0;
  }

  digitalWrite(leftDir, (pwmValLeft>0) );
  digitalWrite(rightDir, (pwmValRight>0) );
  analogWrite(leftWid, abs(pwmValLeft) );
  analogWrite(rightWid, abs(pwmValRight) );
  return;
}

void SetPosiLine(int aimCnt){//only use left encoder
  int leftSpeedInput, rightSpeedInput;
  leftSpeedInput  = PositionPidCal(codeCntLeft, aimCnt, posiPidItg);
  leftSpeedInput  = constrain(leftSpeedInput, -speedMax, speedMax);
  rightSpeedInput = leftSpeedInput;

  SetSpeed(leftSpeedInput,rightSpeedInput);  
  return;
}

void SetDirection(int angle){
  if(aimAngle < 0) aimAngle = aimAngle + 3600;
  if(aimAngle > 3600) aimAngle = aimAngle - 3600;
  //Serial.print("aim: ");
  //Serial.print(aimAngle);
  //Serial.print("  ");
  int angErr = heading - angle;
  //Serial.print("angErr: ");
  //Serial.print(angErr);
  //Serial.print("  ");
  int dirFlag = 1;//1:left -1:right
  if(angErr < 0){
    dirFlag = -dirFlag;
    angErr = -angErr;
  }
  if(angErr > 1800){
    dirFlag = -dirFlag;
    angErr = 3600 - angErr;
  }
  
  
  //Serial.print(dirFlag);
  //Serial.print("  ");
  SetSpeed(-dirFlag*turnSpeed,dirFlag*turnSpeed);
  if(abs(angErr)<angJudge) {
    turnFlag = 0;
    stopFlag = 1;
  }
  return;
}

int SpeedPidCal(int curSpeed, int aimSpeed, PidItgData &itgData){
	int speedErr = aimSpeed - curSpeed, pidOutPut;
	int pidP=0, pidI=0;
  itgData.InsertData(speedErr);
	pidP = int(speedErr*kpSpd);
	pidI = int(itgData.Sum()*kiSpd);
	return pidP + pidI;
}

int PositionPidCal(long curPosi, long aimPosi, PidItgData &itgData){
  int posiErr = aimPosi - curPosi, pidOutPut;
  int pidP=0, pidI=0;
  itgData.InsertData(posiErr);
  pidP = int(posiErr*kpPos);
  pidI = int(itgData.Sum()*kiPos);
  return pidI + pidI;
}
