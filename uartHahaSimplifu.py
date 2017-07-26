

import json
import math
from urllib import request
from vertexTest_mid import *   
#from espeak import espeak
#import evdev
import time
import serial
import syslog, time,sys
import threading

global carLeftSpeed,carRightSpeed,carHeading,carLeftCnt,carRightCnt,carSonar,curSpeed,curHeading
global connectSet,ackSendSet,ackReceiveSet,arriveSet,rcvSet
global deltaSleepTime,maxArriveTime, maxRevTime,deltaSendTime
global flagReceive
flagReceive = 1
carSonar = [0,0,0]
maxArriveTime = 300
maxRevTime = 100

debug = 1
deltaSleepTime = 0.1
deltaSendTime = 0.5
connectSet = 0
ackSendSet = 0
ackReceiveSet = 0 
arriveSet = 1
rcvSet = 0
ser = serial.Serial('/dev/tty.usbmodem1411',115200, timeout=1)

HELLO = bytearray()
HELLO.extend( bytes([0X12]))
ACK = bytearray()
ACK.extend( bytes([0x11]))  #adding bytes to byte array
WORKING = bytearray()
WORKING.extend(bytes([0x13]))
ARRIVE = bytearray()
ARRIVE.extend(bytes([0x18]))
RCV = bytearray()
RCV.extend(bytes([0x20]))
ERROR1 = bytearray()
ERROR1.extend(bytes([0x14]))
MYSTART = bytearray()
MYSTART.extend( bytes([0x5A]))
ARSTART = bytearray()
ARSTART.extend( bytes([0xA5]))
EMPTY = bytearray()
EMPTY.extend(bytes([0x00]))

errorInf = {0:"", 1:"Empty List Now", 2:"Checkpoint Error", 3:"Has not sent ACK but received ACK", 4:"Unknown VNC"}

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print ("Start thread：" + self.name)
        #print_time(self.name, self.counter, 5)
        global graph
        if (self.threadID==1):
            #graph.__SoosNavigate__(route)
            Navigate()
        else:
            #print_time(self.name,5,self.counter)
            ComWithArduino()
    
        print ("Exit thread：" + self.name)


def PrintDebug(resBuf):
    if debug>0:
        if resBuf[1]!=WORKING:
            for i in range(17):
                print(resBuf[i],end=" ")
            print("")
        else:
            print("Working")

def Receive():
    global carLeftSpeed,carRightSpeed,carHeading,carLeftCnt,carRightCnt,carSonar,curSpeed,curHeading
    global connectSet,ackSendSet,ackReceiveSet,arriveSet,rcvSet
    resBuf = [EMPTY for i in range(20)]
    while 1:
        if ser.inWaiting()==0:
            return 1
        resBuf[0] = ser.read()
        if debug>0:
            print(resBuf[0],end=" ")
        if resBuf[0] == ARSTART:
            break

    for i in range(1,17):
        resBuf[i] = ser.read()
    PrintDebug(resBuf)

    if resBuf[1] == HELLO:
        Send(ACK,0,0)
        ackSendSet = 1
    elif resBuf[1] == ACK:
        if ackSendSet == 1:
            connectSet = 1
            print("Connect Success!")
        else:
            return 3
    elif resBuf[1] == RCV:
        rcvSet = 1
    elif resBuf[1] == ARRIVE:
        arriveSet = 1
    elif resBuf[1] == WORKING:
        correctEnd = int.from_bytes(resBuf[15],byteorder='big')+int.from_bytes(ARSTART,byteorder='big')
        if correctEnd != int.from_bytes(resBuf[16],byteorder='big'):
            return 2
        carLeftSpeed = int.from_bytes(resBuf[2],byteorder='big')
        carRightSpeed = int.from_bytes(resBuf[3], byteorder='big')
        carHeading = int.from_bytes(resBuf[4],byteorder='big')
        cnt = bytearray()
        for i in range(5,9):
            cnt.extend( bytes(resBuf[i]))
        carLeftCnt = int.from_bytes(cnt, byteorder='big')
        cnt = bytearray()
        for i in range(9,13):
            cnt.extend( bytes(resBuf[i]))
        carRightCnt = int.from_bytes(cnt, byteorder='big')
        for i in range(13,16):
            carSonar[i-13] = int.from_bytes(resBuf[i],byteorder='big')
    else:
        return 4
    return 0

def Send(state, dist, turnAngle):
    time.sleep(deltaSleepTime)
    ser.write(MYSTART)
    ser.write(state)
    '''
    distH = bytearray()
    distL = bytearray()
    distH = distH.extend(dist.to_bytes(2,byteorder='big')[0])
    distL = distL.extend(dist.to_bytes(2,byteorder='big')[1])
    '''
    distH = int(dist/256)
    distL = dist%256
    ser.write(distH.to_bytes(1,byteorder='big'))
    ser.write(distL.to_bytes(1,byteorder='big'))
    heading = int((turnAngle+180)/2) 
    ser.write(heading.to_bytes(1,byteorder='big'))
    end = (int.from_bytes(MYSTART,byteorder='big')+heading)%256
    ser.write(end.to_bytes(1,byteorder='big'))
    if debug>0:
        print("Sending: ", MYSTART, " ", state, " ", distH," ", distL, " ",heading," ",end)
    time.sleep(deltaSleepTime)

def SendOrder(curDist, turnAngle):
    global arriveSet, rcvSet,maxRevTime, maxArriveTime,flagReceive
    print("Sending order: ", curDist," ",turnAngle)
    iterTimes = 0
    while arriveSet==0:
        time.sleep(deltaSendTime)
        while ser.inWaiting()>0:
            Receive()
            if arriveSet>0:
                break
        iterTimes += 1
        if iterTimes>maxArriveTime:
            print("ERROR! ARRIVE OUT OF TIME")
            break
    print("Last Time has arrived")
    if arriveSet>0:
        rcvSet = 0
        arriveSet = 0
        iterTimes = 0
        while rcvSet == 0:
            Send(WORKING, curDist, turnAngle)
            flagReceive = 0
            while ser.inWaiting()>0:
                Receive()
                if rcvSet>0:
                    break
            time.sleep(deltaSendTime)
            iterTimes += 1
            if iterTimes > maxRevTime:
                print("ERROR! RECEIVE OUT OF TIME")
                break

def Navigate():
    global arriveSet,connectSet, curDist, turnAngle
   # while connectSet==0:
   #     time.sleep(deltaSleepTime)
    print("Navigate Start")
    time.sleep(1)
    arriveSet = 1
    curDist = 50
    turnAngle = 0
    #SendOrder()
    SendOrder(50,0)
    time.sleep(5)
    curDist = 0
    turnAngle = 90
    #SendOrder()
    SendOrder(0,90)

def ComWithArduino():
    i = 0
    global  curDist, turnAngle,flagReceive
    try:
        while connectSet == 0:
            errorID = Receive()
            print(errorInf[errorID])
            time.sleep(deltaSleepTime)
    except KeyboardInterrupt:
        ser.close()

ComWithArduino()
Navigate()




