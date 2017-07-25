#define HELLO 0x12
#define ACK 0x11
#define WORKING 0x13
#define  ERROR1 0x14

#define BYTE0(dwTemp)       ( *( (char *)(&dwTemp)	  ) )
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

void setup()
{
	Serial.begin(115200);
  Serial1.begin(9600);
}

void loop()
{
	SendData(WORKING);
	delay(500);
  Serial1.print("state:");
  Serial1.print(connectSet);
	if(ReceiveData() == 0){
    Serial1.print(" sp:");
    Serial1.print(aimSpeed);
    Serial1.print(" agl:");
    Serial1.print(aimAngle);
	}
  Serial1.println("");
  delay(500);
}

void SendData(char state){
	unsigned char sum = 0xA5;
	Serial.write(0xA5);
	if(connectSet == 0){
		state = HELLO;
	}
	Serial.write(char(state));
	if(state == WORKING){
		Serial.write(char(speed));
		Serial.write(char(heading/20));
		Serial.write(BYTE3(codeCnt));
		Serial.write(BYTE2(codeCnt));
		Serial.write(BYTE1(codeCnt));
		Serial.write(BYTE0(codeCnt));
		Serial.write(BYTE0(sonar0));
		Serial.write(BYTE0(sonar1));
		Serial.write(BYTE0(sonar2));
		sum += BYTE0(sonar2);
		Serial.write(sum);
	}
	else{
		Serial.write(0x0);
		Serial.write(0x0);
		Serial.write(0x0);
		Serial.write(0x0);
		Serial.write(0x0);
		Serial.write(0x0);
		Serial.write(0x0);
		Serial.write(0x0);
		Serial.write(0x0);
		sum += 0x0;
		Serial.write(sum);
	}
}

int ReceiveData(){
	unsigned char c;
  char cc;
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
        c = Serial.read();
	      aimSpeedBuf = int(c)-127;
	      c = Serial.read();
	      aimAngleBuf = int(c*20);
	      c += 0x5A;
	      if(c == Serial.read()){
	      	aimSpeed = aimSpeedBuf;
	      	aimAngle = aimAngleBuf;
	      }
	      else connectSet = 0;
	      break;

	    default:
        connectSet = 0;
	      break;
	}
	return 0;
}
