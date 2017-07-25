import serial
import syslog, time,sys
ser = serial.Serial('/dev/tty.usbmodem1411', 115200, timeout=1)

ser.write("testing serial connection\n".encode('utf-8'))
ser.write("sending via RPi\n".encode('utf-8'))

HELLO = bytearray()
HELLO.extend( bytes([0X12]))
ACK = bytearray()
ACK.extend( bytes([0x11]))  #adding bytes to byte array
RIGHT = bytearray()
RIGHT.extend(bytes([0x13]))
MYSTART = bytearray()
MYSTART.extend( bytes([0x5A]))
ARSTART = bytearray()
ARSTART.extend( bytes([0xA5]))
deltaSleepTime = 0.1
debug = 1
global state
global arduinoSpeed
global arduinoHeading
global arduinoCnt
global arduinoSonar
global curSpeed
global curHeading
arduinoSonar = [ 0, 0, 0]
curHeading = 180
curSpeed = 3
def HandShake():
    while 1:
        response = ser.read()
        if response == HELLO:
            ser.write(ACK)
            print("response: HELLO")
            print("sending: ",ACK)
        if response == ACK:
            ser.write(RIGHT) 
            print("response: ACK")
            print("sending: ", RIGHT)
            break
        time.sleep(0.1)
        

def UpdateState():
    response = ser.read()
    '''
    while response==HELLO:
        HandShake()
        response = ser.read()
        '''
    state = response
    print("Updated State: ",state)

def UpdateSpeed():
    response = ser.read()
    print("response speed: ",response )
    arduinoSpeed = int.from_bytes(response, byteorder='big')
    if (arduinoSpeed>127):
        arduinoSpeed = arduinoSpeed - 256
    print("Arduino speed: ",arduinoSpeed)
    # arduinoSpeed = int.from_bytes(response, byteorder='big')ValueError: invalid literal for int() with base 16: b'\xf6'


def UpdateCnt():
    cnt = bytearray()
    for i in range(4):
        response = ser.read()
        cnt.extend( bytes(response))
    arduinoCnt = int.from_bytes(cnt, byteorder='big')
    print("Arduino Cnt: ",arduinoCnt)

def UpdateHeading():
    response = ser.read()
    arduinoHeading = int.from_bytes(response, byteorder='big')
    print("response heading: ", response)
    print("Arduino heading: ",arduinoHeading)

def UpdateSonar():
    for i in range(0,3):
        response = ser.read()
        arduinoSonar[i] = int.from_bytes(response, byteorder='big')
        print("Arduino Sonar[",i,"]: ",arduinoSonar[i])

def JudgeCorrect():
    response = ser.read()  
    end = int.from_bytes(response, byteorder='big')
    arduinoSonar[2] + int.from_bytes(ARSTART,byteorder='big')
    if response!=


def SendMsg():
    ser.write(MYSTART)
    ser.write(RIGHT)
    ser.write(curSpeed.to_bytes(1, byteorder='big'))
    ser.write(curHeading.to_bytes(1,byteorder='big'))
    end = (int.from_bytes(MYSTART,byteorder='big')+curHeading)%256
    #ser.write(MYSTART+curHeading.to_bytes(1,byteorder='big'))
    ser.write(end.to_bytes(1,byteorder='big'))
    print("Sending End: ",end)

HandShake()
try:
    while 1:
        response = ser.read()
        print("response: ",response)
        if response==ARSTART:
            time.sleep(deltaSleepTime)
            UpdateState()
            UpdateSpeed()
            UpdateHeading()
            UpdateCnt()
            UpdateSonar()
            JudgeCorrect()
        SendMsg()  
        time.sleep(0.1)
except KeyboardInterrupt:
    ser.close()

