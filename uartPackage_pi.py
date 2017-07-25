import serial
import syslog, time,sys
ser = serial.Serial('/dev/tty.usbmodem1411',115200, timeout=1)

#ser.write("testing serial connection\n".encode('utf-8'))
#ser.write("sending via RPi\n".encode('utf-8'))

HELLO = bytearray()
HELLO.extend( bytes([0X12]))
ACK = bytearray()
ACK.extend( bytes([0x11]))  #adding bytes to byte array
WORKING = bytearray()
WORKING.extend(bytes([0x13]))
ERROR1 = bytearray()
ERROR1.extend(bytes([0x14]))
MYSTART = bytearray()
MYSTART.extend( bytes([0x5A]))
ARSTART = bytearray()
ARSTART.extend( bytes([0xA5]))
EMPTY = bytearray()
EMPTY.extend(bytes([0x00]))
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
curHeading = 1
curSpeed = 127-3
def HandShake():
    while 1:
        response = ser.read()
        print("response: ", response)
        if response == HELLO:
            #ser.write(ACK)
            SendMsg(ACK)
            print("response: HELLO")
            #print("sending: ",ACK)
        if response == ACK:
            #ser.write(WORKING) 
            SendMsg(WORKING)
            print("response: ACK Handshake Success!")
            #print("sending: ", WORKING)
            break
        time.sleep(deltaSleepTime)
        

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
    correctEnd = arduinoSonar[2]+int.from_bytes(ARSTART,byteorder='big')
    if end!=correctEnd:
        arduinoSpeed = curSpeed
        arduinoHeading = curHeading
        SendMsg(ERROR1)

def SendMsg(state):
    if (state==WORKING):
        global curSpeed
        curSpeed = (curSpeed + 1)%256
        global curHeading  
        curHeading = (curHeading + 1)%256
        ser.write(MYSTART)
        print("sending: ",MYSTART)
        ser.write(WORKING)
        print("sending: ",WORKING)
        ser.write(curSpeed.to_bytes(1, byteorder='big'))
        print("sending: ",curSpeed.to_bytes(1, byteorder='big'))
        ser.write(curHeading.to_bytes(1,byteorder='big'))
        print("sending: ",curHeading.to_bytes(1, byteorder='big'))
        end = (int.from_bytes(MYSTART,byteorder='big')+curHeading)%256
        #ser.write(MYSTART+curHeading.to_bytes(1,byteorder='big'))
        ser.write(end.to_bytes(1,byteorder='big'))
        print("Sending End: ",end)
    elif (state==ACK):
        ser.write(MYSTART)
        print("sending: ",MYSTART)
        ser.write(ACK)
        print("sending: ",ACK)
        ser.write(EMPTY)
        print("sending: ",EMPTY)
        ser.write(EMPTY)
        print("sending: ",EMPTY)
        ser.write(MYSTART)
        print("Sending End: ",MYSTART)
    else:
        ser.write(MYSTART)
        print("sending: ",MYSTART)
        ser.write(ERROR1)
        print("sending ERROR!!!!!!!!!")
        ser.write(EMPTY)
        print("sending: ",EMPTY)
        ser.write(EMPTY)
        print("sending: ",EMPTY)
        ser.write(MYSTART)
        print("Sending End: ",MYSTART)

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
        SendMsg(WORKING)  
        time.sleep(deltaSleepTime)
except KeyboardInterrupt:
    ser.close()