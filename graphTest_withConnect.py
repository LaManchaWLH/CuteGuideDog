
import json
import math
from urllib import request
from vertexTest_mid import *   
#from espeak import espeak
#import evdev

debug = 0   # to check whether to print the debug information


class Graph(object):

    def __init__(self, mapJson):

        #To define the constants
        self.pointsInfo = {}
        maxNodeNum = 100
        self.Infinity = 100000
        self.maxDeltaAngle = math.pi / 9
        self.firstInformDist = 200
        self.secondInformDist = 100
        self.maxDeltaDist = 15
        self.maxValidDist = 5000
        self.nodeNum = len(mapJson["map"])
        
        #To initiate the points of the graph
        for i in range(0, self.nodeNum):
            tempVertex = Vertex(mapJson["map"][i]["nodeName"],mapJson["map"][i]["x"],mapJson["map"][i]["y"])
            self.pointsInfo[int(mapJson["map"][i]["nodeId"])] = tempVertex 

        #To initiate the ajacency matrix of the graph
        self.adjMatrix = [[self.Infinity for i in range(maxNodeNum)] for j in range(maxNodeNum)]
        for i in range(0, self.nodeNum):
            self.adjMatrix[i+1][i+1] = 0       
            j = 0
            if (debug):
                print("link is ",mapJson["map"][i]["linkTo"])
            linkList = mapJson["map"][i]["linkTo"].split(",")
            linkNum = len(linkList)
            if (debug):
                print("linkNum is ",linkNum)
            for j in range(0,linkNum):
                id1 = i+1
                id2 = int(linkList[j])
                if (debug):
                    print(id1," ",id2)
                point1 = self.pointsInfo[id1]
                point2 = self.pointsInfo[id2]
                dis = Vertex.dist__(point1,point2)
                self.adjMatrix[id1][id2] = dis

    #To print the debug information of the graph
    def __str__(self):
        print("There are %d nodes in sum. Their info is shown as below"%(self.nodeNum))
        for i in range(1, self.nodeNum+1):
            self.pointsInfo[i].__print__()
        print("The adjacency matrix is shown as below")
        for i in range(1, self.nodeNum+1):
            print(self.adjMatrix[i][1:self.nodeNum+1])

    #To show the turning information for the user
    def __TurnInf__(self,angle):
        if angle>self.maxDeltaAngle:
            turnInf = "Please turn right for "+str(int(angle))+" degrees "
        elif angle < (-1)*self.maxDeltaAngle:
            turnInf = "Please turn left for " + str(int(-angle)) + " degrees "
        else:
            turnInf = "Please go straight"
        return turnInf 

    #To calculate the shortest route using dijkstra
    def __Dijkstra__(self, startPoint, destPoint):

        #initiate
        prev = [-1 for i in range(self.nodeNum+2)]              #prev[i] means the previous point before visiting i 
        hasVisited = [0 for i in range(self.nodeNum+2)]         #hasVisited[i] means whether point i has been visited
        dist = [self.Infinity for i in range(self.nodeNum+2)]   #dist[i] means the shortest distance between i and star tPoint
        dist[startPoint] = 0
        for i in range(1, self.nodeNum+1):
            if dist[i]!=self.Infinity:
                prev[i] = startPoint
        prev[startPoint] = 0

        #dijkstra
        for j in range(self.nodeNum):
            minDist = self.Infinity
            for i in range(1,self.nodeNum+1):                   #find the min distance
                if hasVisited[i]==0 and dist[i]<minDist:
                    minID = i
                    minDist = dist[i]
            hasVisited[minID] = 1                               # mark minID has been visited     
            for i in range(1, self.nodeNum+1):                  # update
                if hasVisited[i]==0 and dist[minID]+self.adjMatrix[minID][i]<dist[i]:
                    dist[i] = dist[minID]+self.adjMatrix[minID][i]
                    prev[i] = minID
        route = []
        if (debug):
            print("hasVisited: ",hasVisited)
            print("dist to startPoint is ", dist[1:self.nodeNum+1])
            print("previous point list is ",prev)
        tempNode = destPoint
        while prev[tempNode]!=0:                                #transform prev[] to route[]
            route.append(tempNode)
            tempNode = prev[tempNode]
        route.append(startPoint)
        route.append(dist[destPoint])
        if (debug):
            print("In detail, the route is ",route)
        route.reverse()
        return route

    def TransformAngle(heading):
        return (-1*heading + 90) 

    def __SoosNavigate__(self,route):

        #initiate p.s. The userPos data is built upon DemoBuilding level1 3->5
        #userPos =  [{"x":400,"y":200,"heading":0}, {"x":500,"y":200,"heading":90},{"x":595,"y":200,"heading":90},
        #{"x":600,"y":300,"heading":0},{"x":600,"y":486,"heading":10}]
        curRouteId = 1
        nextRouteId = curRouteId+1
        totalRoute = len(route)-1
        #posId = 0
        
        while 1>0:
            #curX = userPos[posId]["x"] 
            #curY = userPos[posId]["y"] 
            #curAngle = Graph.TransformAngle(userPos[posId]["heading"])
            curX = ReadNum("Plz input your current x: ")
            curY = ReadNum("Plz input your current y: ")
            curAngle = Graph.TransformAngle(ReadNum("Plz input your current heading: "))
            curDist = Vertex.dist__(curX, curY, self.pointsInfo[route[nextRouteId]].x, self.pointsInfo[route[nextRouteId]].y)
            if (curDist<self.maxDeltaDist):         
                msg="Congratulations! You have reached "+ self.pointsInfo[route[nextRouteId]].name+"! "
                print(msg)
                espeak.synth(msg)
                curRouteId = nextRouteId
                if (curRouteId == totalRoute):
                    msg1="This is your destination. "
                    msg2 = "Please stop now."
                    print(msg1, msg2)
                    espeak.synth(msg1)
                    espeak.synth(msg2)
                    break
                nextRouteId = nextRouteId + 1
                curDist = Vertex.dist__(curX, curY, self.pointsInfo[route[nextRouteId]].x, self.pointsInfo[route[nextRouteId]].y)
            tempVertex = Vertex("temp",curX, curY)
            aimedAngle = int(Vertex.angle__(tempVertex, self.pointsInfo[route[nextRouteId]]))
            turningAngle = (curAngle - aimedAngle) % 360
            if abs(turningAngle)>180:
                if turningAngle>0:
                    turningAngle = turningAngle - 360
                else:
                    turningAngle = 360 + turningAngle
            msg1 = self.__TurnInf__(turningAngle)
            msg2 = " The remaining distance is "+str(int(curDist))
            print(msg1,msg2)
            espeak.synth(msg1)
            espeak.synth(msg2)
            if (curDist>self.maxValidDist):
                print("Error! Might be out of map!")

    def __FindConnectPoint__(self, building, level):
        connect = [-1, -1]
        for i in range(1,self.nodeNum+1):
            name = self.pointsInfo[i].name
            if "TO" in name:
                if debug>0:
                    print(name)
                name = (name.split(" "))[1]
                if "-" in name:
                    [linkBuild, linkLevel, linkNode] = name.split("-")
                    if building==linkBuild or "COM"+building == linkBuild:
                        if level == linkLevel:
                            connect = [i, linkNode]
                            break
        return connect
            
'''
def ReadNum(text):
    print(text)
    dev = evdev.InputDevice('/dev/input/event0')
    eventNode = {79:"1",80:"2",81:"3",75:"4",76:"5",77:"6",71:"7",72:"8",73:"9",82:"0",96:"e"}
    str = ""
    for event in dev.read_loop():
        if (event.value == 1):
            if event.code == 96:
                break
            else:
                str = str + eventNode[event.code]
    num = int(str)
    print(num)
    return num
#Download the map

building = str(ReadNum("Plz input your building name: "))
#buildingList = [1,2,3]
#buildingMap = {"1":"COM1", "2":"COM2", "3":"DemoBuilding"}
#while (building in buildingList) == 0:
#    building = ReadNum("This building does not exist!. Plz input your building name again: ")
#building = buildingMap[str(building)]
level = str(ReadNum("Plz input your level: "))
#building = "DemoBuilding"
#sslevel = "1"
with request.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building='+building+'&Level='+level) as f:
    data= f.read()
mapJson = json.loads(data.decode('utf-8'))
print("The number of nodes is %d"%(len(mapJson["map"])))
print("The name of the first node is", mapJson["map"][0]["nodeName"])

#save the json file
filename = str(ReadNum("Plz input your wanted filename: "))
with open(filename+".json",'w') as file:
    json.dump(mapJson,file)

#get the shortest path and navigate
graph = Graph(mapJson)
if debug:
    graph.__str__()
startPoint = int(ReadNum("Plz input your starting place: "))
destPoint = int(ReadNum("Plz input your destination: "))
route = graph.__Dijkstra__(startPoint, destPoint)
espeak.synth("Navigation now starts")
graph.__SoosNavigate__(route)
espeak.synth("Goodbye")
'''




