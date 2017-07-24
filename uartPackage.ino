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
}

void loop()
{
	SendData();
	delay(100);
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
	int aimSpeedBuf,aimAngleBuf;
	if(Serial.available() != 0){
		if(Serial.readBytesUntil(0x5A) != 0){
			c = Serial.read();
			switch (c) {
			    case : ACK
			      SendData(ACK);
			      connectSet = 1;
			      break;

			    case : WORKING
			      aimSpeedBuf = int(Serial.read());
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
			      // do something
			}
		}
		else return 1;
	}
	else return 1;

	return 0;
}