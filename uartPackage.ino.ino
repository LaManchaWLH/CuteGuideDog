#define HELLO 0x12
#define ACK 0x11
#define WORKING 0x13
#define  ERROR1 0x14

#define BYTE0(dwTemp)       ( *( (char *)(&dwTemp)    ) )
#define BYTE1(dwTemp)       ( *( (char *)(&dwTemp) + 1) )
#define BYTE2(dwTemp)       ( *( (char *)(&dwTemp) + 2) )
#define BYTE3(dwTemp)       ( *( (char *)(&dwTemp) + 3) )

int speed = -10;
int aimSpeed = 0;
int heading = 2700;
int aimAngle = 0;
long codeCnt = 23123;
int sonar0 = 150;
int sonar1 = 111;
int sonar2 = 24;
bool connectSet = 0;


int p1 = 3;// test added
int p2 = 260;


int iterTimes = 0;

void HandShake()
{
  if (!Serial.available())
  {
    while (1){
      if (Serial.available()){
        int inByte = Serial.read();
        //Serial.write(inByte);
        if (inByte==WORKING)
        {
          Serial.write("SUCCESS");
          break;
        }
        else if (inByte==ACK)
        {
          Serial.write(ACK);
        } else
        {
          Serial.write(HELLO);
        }
      }
      delay(100);
    }
  }
  connectSet = 1;
}

void setup()
{
  Serial.begin(115200);
  HandShake();
  Serial.write("Starts:");
  
}

void loop()
{
  if (iterTimes<5)
  {
    SendData(WORKING);
    delay(100);
    ReceiveData(WORKING);
    delay(100);
    iterTimes++;
    codeCnt++;
  }
  
}

void SendData(char state){
  unsigned char sum = 0xA5;
  unsigned char cc;
  Serial.write(0xA5);
  connectSet = 1; // test addeds
  if(connectSet == 0){
    state = HELLO;
  }
  Serial.write(char(state));
  if(state == WORKING){
    //test starts
    cc = speed;Serial.write(cc);
    cc = heading/20;Serial.write(cc);
    Serial.write(BYTE3(codeCnt));
    Serial.write(BYTE2(codeCnt));
    Serial.write(BYTE1(codeCnt));
    Serial.write(BYTE0(codeCnt));
    Serial.write(BYTE0(sonar0));
    Serial.write(BYTE0(sonar1));
    Serial.write(BYTE0(sonar2));
    sum += BYTE0(sonar2);
    if (iterTimes==2) Serial.write(0x01);
              else    Serial.write(sum); // test adds
    
  }
  else{
    Serial.write(0x11);
    Serial.write(0x22);
    Serial.write(0x33);
    Serial.write(0x44);
    Serial.write(0x55);
    Serial.write(0x66);
    Serial.write(0x77);
    Serial.write(0x88);
    Serial.write(0x99);
    sum += 0x99;
    Serial.write(sum);
  }
}

int ReceiveData(int state){
  unsigned char c;
  char cc,ccb;
  int aimSpeedBuf,aimAngleBuf;
  
  while(1){
    if(Serial.read() == 0x5A) break;
    if(Serial.available() == 0) return 1;
  }
  c = Serial.read();
 
  switch (c) {
      case ACK: 
        SendData(ACK);
        connectSet = 1;
        break;

      case WORKING: 
        cc = Serial.read();
        aimSpeedBuf = int(cc);
        cc = Serial.read();
        aimAngleBuf = int(cc*20);
        cc += 0x5A;
        ccb = Serial.read();
        if(cc == ccb){
          aimSpeed = aimSpeedBuf;
          aimAngle = aimAngleBuf;

          // testing part
          
          speed = aimSpeed;
          heading = aimAngle;
        }
        else connectSet = 0;
        break;

      default:
        break;
  }
  return 0;
}
