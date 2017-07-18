#define leftDir 7
#define rightDir 4
#define leftWid 6
#define rightWid 5
#define fullSpeed 230
#define midSpeed 120
#define lowSpeed 100

void setup() {
  pinMode(LED_BUILTIN,OUTPUT);
  pinMode(leftDir,OUTPUT);
  pinMode(rightDir,OUTPUT);
  pinMode(leftWid,OUTPUT);
  pinMode(rightDir,OUTPUT);
  //randomSeed(analogRead(0));
  Serial.begin(9600);
}

int leftDirVal=0, rightDirVal=0, leftWidVal=0, rightWidVal=0;
void loop() {
  // put your main code here, to run repeatedly:
   digitalWrite(leftDir,leftDirVal);
   digitalWrite(rightDir,rightDirVal);
   analogWrite(leftWid,leftWidVal);
   analogWrite(rightWid,rightWidVal);
}

void serialEvent(){
   char a = Serial.read(); 
    Serial.println(a);
    if(a == 'w') {
      leftDirVal = 1;
      rightDirVal = 1;
      leftWidVal = fullSpeed;
      rightWidVal = fullSpeed;
    }
    else if(a == 's'){
      leftDirVal = 0;
      rightDirVal = 0;
      leftWidVal = fullSpeed;
      rightWidVal = fullSpeed;
    }
    else if(a == 'a'){
      leftDirVal = 0;
      rightDirVal = 1;
      leftWidVal = fullSpeed;
      rightWidVal = fullSpeed;
    }
    else if(a == 'd'){
      leftDirVal = 1;
      rightDirVal = 0;
      leftWidVal = fullSpeed;
      rightWidVal = fullSpeed;
    }
    else{
      leftDirVal = 1;
      rightDirVal = 1;
      leftWidVal = 0;
      rightWidVal = 0;
    }
}
