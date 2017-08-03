import json
import math
from urllib import request
from vertexTest_mid import *   
from graphTest_withConnect import *
from espeak import espeak
import evdev
import time,pygame
import serial
import syslog, time,sys,os
import threading
import subprocess
global carLeftSpeed,carRightSpeed,carHeading,carLeftCnt,carRightCnt,carSonar,curSpeed,curHeading
global connectSet,ackSendSet,ackReceiveSet,arriveSet,rcvSet
global deltaSleepTime,maxArriveTime,deltaSpeakTime,maxRevTime,deltaSendTime
global autoInputFlag,flagReceive, maxIterTimes,Indoor, Outdoor
global building, buildingDest, level, levelDest, flagKua, flagIndoor, startPoint, destPoint
global ser,debug,dd
global indoorList, outdoorList, checkList
autoInputFlag = 1
indoorList = [11,14,26, 32]
outdoorList = [17, 10]
checkList = [ 11,  2]
flagReceive = 1
carSonar = [0,0,0]
maxArriveTime = 300
maxRevTime = 100
debug = 0
deltaSleepTime = 0.1
deltaSendTime = 0.5
connectSet = 0
ackSendSet = 0
ackReceiveSet = 0 
arriveSet = 1
rcvSet = 0
maxIterTimes = 4
Indoor = -2
Outdoor = -1
flagKua = 0
flagIndoor = 1
#ser = serial.Serial('/dev/tty.usbmodem1411',115200, timeout=1)
#ser = serial.Serial('/dev/serial/by-id/usb-Arduino_Srl_Arduino_Mega_85430353331351103221-if00',115200, timeout=1)

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
MYSTART.extend( bytes([0xFE]))
ARSTART = bytearray()
ARSTART.extend( bytes([0xA5]))
NORTH = bytearray()
NORTH.extend(bytes([0x23]))
EMPTY = bytearray()
EMPTY.extend(bytes([0x00]))
INDOOR = bytearray()
INDOOR.extend(bytes([0x24]))
OUTDOOR = bytearray()
OUTDOOR.extend(bytes([0x25]))
dd = 1340

errorInf = {0:"", 1:"Empty List Now", 2:"Checkpoint Error", 3:"Has not sent ACK but received ACK", 4:"Unknown VNC"}

def PrintDebug(resBuf):
    if debug>0:
        if resBuf[1]==HELLO:
            print("HELLO")
        elif resBuf[1]==ACK:
            print("ACK")
        else:
            for i in range(17):
                print(resBuf[i],end=" ")
            print("")

def speak(txt):
    espeak.synth(txt)
    time.sleep(1)
    '''
    tts = gTTS(text=txt)
    tts.save("tts.mp3")
    time.sleep(0.5)
    track = pygame.mixer.music.load("tts.mp3")
    pygame.mixer.music.play()
    time.sleep(0.5)
    '''
    #subprocess.Popen('espeak -v+f2 -s200 -g12 "'+txt+'"',shell=True, executable='/bin/bash')
    #time.sleep(2)
    
def music(musicName):
    track = pygame.mixer.music.load(musicName+".mp3")
    pygame.mixer.music.play()
    time.sleep(8)

def Receive():
    global carLeftSpeed,carRightSpeed,carHeading,carLeftCnt,carRightCnt,carSonar,curSpeed,curHeading
    global connectSet,ackSendSet,ackReceiveSet,arriveSet,rcvSet
    resBuf = [EMPTY for i in range(20)]
    errorID = 0

    while 1:
        if ser.inWaiting()==0:
            errorID = 1
            break
        resBuf[0] = ser.read()
        if debug>0:
            print(resBuf[0],end=" ")
        if resBuf[0] == ARSTART:
            break

    if errorID == 0:
        for i in range(1,17):
            resBuf[i] = ser.read()
        PrintDebug(resBuf)

        if resBuf[1] == HELLO:
            if connectSet==0:
                Send(ACK,0,0)
            ser.flushInput()
            ackSendSet = 1
            connectSet = 1
            print("Presume Connect Success!")

        elif resBuf[1] == ACK:
            if ackSendSet == 1:
                connectSet = 1
                print("Connect Success!")
            else:
                errorID = 3

        elif resBuf[1] == RCV:
            rcvSet = 1

        elif resBuf[1] == ARRIVE:
            speak("yeah")
            print("yeah")
            arriveSet = 1

        elif resBuf[1] == WORKING:
            correctEnd = int.from_bytes(resBuf[15],byteorder='big')+int.from_bytes(ARSTART,byteorder='big')
            if correctEnd != int.from_bytes(resBuf[16],byteorder='big'):
                errorID = 2
            else:
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
            errorID = 4
    return errorID

def Send(state, dist, turnAngle):
    time.sleep(deltaSleepTime)
    #ser.flushOutput()
    ser.write(MYSTART)
    print(MYSTART,end=" ")
    ser.write(state)
    print(state,end=" ")
    distH = int(dist/256)
    distL = dist%256
    ser.write(distH.to_bytes(1,byteorder='big'))
    ser.write(distL.to_bytes(1,byteorder='big'))
    print("distH:",distH," distL:",distL)
    if state==NORTH:
        heading = int(((turnAngle+360)%360)*0.5)
    else:
        heading = int((turnAngle+180)/2) 
    ser.write(heading.to_bytes(1,byteorder='big'))
    end = (int.from_bytes(MYSTART,byteorder='big')+heading)%256
    ser.write(end.to_bytes(1,byteorder='big'))
    if 1:
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

    if turnAngle>0:
        speak("Arrive")

    if curDist==0 and turnAngle==0:
        print("will do nothing")
    else:
        if curDist == -1:
            arriveSet=0
            if turnAngle == Indoor:
                print("Will Send Indoor signal")
                Send(INDOOR, 0,0)
            else:
                print("Will Send Outdoor signal")
                Send(OUTDOOR,0,0)
        elif curDist == -2:
            arriveSet = 0
            Send(NORTH, 0, turnAngle)
        else:
            if connectSet == 1:
                arriveSet = 0
                Send(WORKING, curDist, turnAngle)
            else:
                print("ERROR! SHOULD SEND MSG BUT NOT CONNECT!")
    time.sleep(deltaSendTime)

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


def CalTurningAngle(curAngle,aimedAngle):
    turningAngle = (curAngle - aimedAngle) % 360
    if abs(turningAngle)>180:
        if turningAngle>0:
            turningAngle = turningAngle - 360
        else:
            turningAngle = 360 + turningAngle
    return turningAngle
    
def Navigation(graph, route):
    curRouteId = 1
    nextRouteId = curRouteId+1
    totalRoute = len(route)-1
    turnAngle = [0 for i in range(100)]
    aimAngle = [0 for i in range(100)]
    walkDist = [0 for i in range(100)]
    aimAngle[0] = 135
    print(route)
    for i in range(1,totalRoute):
        aimAngle[i] = int(Vertex.angle__(graph.pointsInfo[route[i]], graph.pointsInfo[route[i+1]]))
        turnAngle[i] = CalTurningAngle(aimAngle[i-1], aimAngle[i])
        walkDist[i] = int(Vertex.dist__(graph.pointsInfo[route[i]],graph.pointsInfo[route[i+1]]))
        if walkDist[i]==649:
            walkDist[i] -= 120
        if route[i]==11:
            turnAngle[i] = -35
        if route[i]==2:
            turnAngle[i] = -35
        print("walkDist[",i,"]=",walkDist[i])
    while curRouteId<totalRoute:
        print("curRouteID", curRouteId)
        temp = graph.pointsInfo[route[curRouteId]]
        print("At: ", temp.x, " ", temp.y," ",temp.name)
        if route[curRouteId] in checkList:
            SendOrder(-2,0)
        SendOrder(0,turnAngle[curRouteId])
        '''
        if route[curRouteId] in checkList:
            if route[curRouteId] == 11 or route[curRouteId] == 2:
                SendOrder(-2, -35)
            else:
                SendOrder(-2, 135-aimAngle[curRouteId])
    
            if abs(turnAngle[curRouteId])>10:
                SendOrder(0, turnAngle[curRouteId])
        '''
        if route[curRouteId] in indoorList:
            SendOrder(-1,Indoor)
        if route[curRouteId] in outdoorList:
            SendOrder(-1, Outdoor)
        if flagIndoor>0:
            d = walkDist[curRouteId]
            while d>dd:
                SendOrder(dd,0)
                d -=dd
            if d>0:
                SendOrder(d,0)
        else:
            SendOrder(walkDist[curRouteId],0)
        time.sleep(int(walkDist[curRouteId]/60))
        curRouteId += 1
    SendOrder(0,0)

def ReadNum(text):
    dev = evdev.InputDevice('/dev/input/event0')
    eventNode = {79:"1",80:"2",81:"3",75:"4",76:"5",77:"6",71:"7",72:"8",73:"9",82:"0",96:"e"}
    str = ""
    print(text)
    iterTimes = 0 
    num = -1
    while 1>0:
        flag = 1 # first defined to be true means no bug
        iterTimes += 1
        if iterTimes > maxIterTimes:
            speak("Sorry! There might be bugs with keyboard")
            break
        str = ""
        for event in dev.read_loop():
            if (event.value == 1):
                if event.code == 96:
                    break
                else:
                    if event.code in eventNode:
                        str = str + eventNode[event.code]
                    else:
                        print("ERROR!The code of your recent input (",event.code,") is Invalid")
                        flag = 0
        if flag:
            num = int(str)
            break
        else:
            speak("ERROR! Please input again")
            print("Try again.",text)
    print(num)
    return num

def GetMapJson(building, level):
    pwd = sys.path[0]
    if os.path.isfile(pwd):
        pwd = os.path.dirname(pwd)
    print("pwd: ",pwd)
    fileName = pwd + '/map/' + building + '_' + level + '.json'
    if os.path.isfile(fileName):
        with open(fileName,'r') as file:
            contents = file.read()
        mapJson = json.loads(contents)
        print("mapJson: ",mapJson)   #这里+break， 加上上面的封装一个函数吧
    else:
        print("ERROR! the map of your building and level doesn't exist")
        speak("Map don't exist!")
    return mapJson

def UpdateInput():
    global building, buildingDest, level, levelDest, flagKua, startPoint, destPoint
    speak("Input building please")
    building = str(ReadNum("Plz input your building name: "))
    time.sleep(4)
    speak("Input end building please")
    buildingDest = str(ReadNum("Plz input your end building name: "))
    if building == buildingDest:
        speak("Input level please")
        level = str(ReadNum("Plz input your level: "))
    else:
        flagKua = 1
        speak("Input starting level please")
        level = str(ReadNum("Plz input your starting level: "))
        speak("Input end level please")
        levelDest = str(ReadNum("Plz input your end level: "))
    speak("Input starting point please")
    startPoint = ReadNum("Plz input your starting place: ")
    speak("Input destination please")
    destPoint = ReadNum("Plz input your destination: ")

pygame.mixer.init()

speak("Input building please")
building = str(ReadNum("Plz input your building name: "))
time.sleep(4)

speak("Input end building please")
buildingDest = str(ReadNum("Plz input your end building name: "))

if building == buildingDest:
    speak("Input level please")
    level = str(ReadNum("Plz input your level: "))
else:
    speak("Input starting level please")
    level = str(ReadNum("Plz input your starting level: "))
    speak("Input end level please")
    levelDest = str(ReadNum("Plz input your end level: "))


pwd = sys.path[0]
if os.path.isfile(pwd):
    pwd = os.path.dirname(pwd)
print("pwd: ",pwd)
fileName = pwd + '/map/' + building + '_' + level + '.json'
if os.path.isfile(fileName):
    with open(fileName,'r') as file:
        contents = file.read()
    mapJson = json.loads(contents)
    print("mapJson: ",mapJson)   #这里+break， 加上上面的封装一个函数吧
else:
    print("ERROR! the map of your building and level doesn't exist")
    speak("Map don't exist!")

graph = Graph(mapJson)
if debug:
    graph.__str__()

speak("Input starting point please")
startPoint = ReadNum("Plz input your starting place: ")

speak("Input destination please")
destPoint = ReadNum("Plz input your destination: ")

route = graph.__Dijkstra__(startPoint, destPoint)
time.sleep(2)

ser = serial.Serial('/dev/serial/by-id/usb-Arduino_Srl_Arduino_Mega_85430353331351103221-if00',115200, timeout=1)
speak("Start shaking hands")
ComWithArduino()
arriveSet = 1
speak("Start Find North")
SendOrder(-2,0)
time.sleep(8)
#arriveSet = 1
#speak("Navigation starts")
#music("start")
Navigation(graph,route)
music("end")
#speak("Goodbye")





