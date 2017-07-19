#include <MsTimer2.h>
#include <math.h>
/****** Pin define *******/
#define leftDir 4
#define rightDir 7
#define leftWid 5
#define rightWid 6
#define codeLeft 2
#define codeRight 3

/****** Parameter define ******/
//pid for position
#define kpPos 8
#define kiPos 0
#define kdPos 0
#define IlenPos 10
#define IMaxPos 50
//for speed loop
#define kpSpd 6
#define kiSpd 0.2
#define kdSpd 0
#define IlenSpd 10
#define IMaxSpd 50
#define timeGap 15//ms
//#define speedFixPar 50

#define pwmMax 240//the maximun of pwm output

#define m1 1885
#define dm1 188

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
volatile long codeCntLeft=0,codeCntRight=0;//encoder valu counter
//volatile long aimCntLeft=0,aimCntRight=0;//aim valu
//int difLeftOld[Ilen]={};//

//for speed loop
volatile int leftCurSpeed=0,rightCurSpeed=0;
volatile int leftAimSpeed=0,rightAimSpeed=0;
volatile int pwmValLeft=0,pwmValRight=0;//pwm output
int codeCntLeftOld=0,codeCntRightOld=0;
PidItgData leftSpeedPidItg(IlenSpd),rightSpeedPidItg(IlenSpd);

//volatile int aimDisX=0,curDisX=0;
//volatile int aimDisY=0,curDisY=0;
//volatile int leftDirVal=1, rightDirVal=1;//direction flag
volatile bool stopFlag = 0;

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
  	//aimCntLeft = codeCntLeft + m1;
  	//aimCntRight = codeCntRight + m1;
  	leftAimSpeed += 2;
  	rightAimSpeed += 2;
  }
  else if(a == 's'){
   	stopFlag = 0;//start
    	//aimCntLeft = codeCntLeft - m1;
    	//aimCntRight = codeCntRight - m1;
    leftAimSpeed -= 2;
    rightAimSpeed -= 2;
  }
  else if(a == 'a'){
    stopFlag = 0;//start
  }
  else if(a == 'd'){
  	stopFlag = 0;//start
  	
  }
  else if(a == 'x'){
  	stopFlag = 1;
  }
}

/******main function*******/
void loop()
{ 

  pwmValLeft += SpeedPidCal(leftCurSpeed,leftAimSpeed,leftSpeedPidItg);
  pwmValRight += SpeedPidCal(rightCurSpeed,rightAimSpeed,rightSpeedPidItg);
  pwmValLeft = constrain(pwmValLeft, -255, 255);
  pwmValRight = constrain(pwmValRight, -255, 255);

  if(stopFlag){
    pwmValLeft = 0;
    pwmValRight = 0;
  }

  digitalWrite(leftDir, (pwmValLeft>0) );
  digitalWrite(rightDir, (pwmValRight>0) );
  analogWrite(leftWid, abs(pwmValLeft) );
  analogWrite(rightWid, abs(pwmValRight) );

  Serial1.print("Ec: ");
  Serial1.print(codeCntLeft);
  Serial1.print("  ");
  Serial1.print(codeCntRight);
  Serial1.println("");
  Serial1.print("Sp: ");
  Serial1.print(leftCurSpeed);
  Serial1.print("  ");
  Serial1.print(rightCurSpeed);
  Serial1.print("  Aim: ");
  Serial1.print(leftAimSpeed);
  Serial1.print("  ");
  Serial1.print(rightAimSpeed);
  Serial1.println("");
}

void SpeedUpdate(){
  leftCurSpeed = (codeCntLeft - codeCntLeftOld);
  rightCurSpeed = (codeCntRight - codeCntRightOld);
	codeCntLeftOld = codeCntLeft;//update old data
	codeCntRightOld = codeCntRight;
  //digitalWrite(13, codeCntLeft % 2);
}

int SpeedPidCal(int curSpeed,int aimSpeed,PidItgData &itgData){
	int speedErr = aimSpeed - curSpeed,pidOutPut;
	int pidP=0,pidI=0,sum;
  itgData.InsertData(speedErr);
	pidP = int(speedErr*kpSpd);
	pidI = int(itgData.Sum()*kiSpd);
	return pidP+pidI;
}
