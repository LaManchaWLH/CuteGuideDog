#learn how to import your own code
#need to import vertexTest.py in some ways
#http://bookshadow.com/weblog/2015/01/08/python-multi-dimensional-arrays-matrices/
import json
import math
from urllib import request
from vertexTest import *   

def sortNode(mapJson):
    num = len(mapJson["map"])
    print("before: ",mapJson["map"])
    for i in range(0,num):
        j = i-1
        curNode = mapJson["map"][i]
        while j>=0:
            if mapJson["map"][j]["nodeId"]>curNode["nodeId"]:
                mapJson["map"][j+1] = mapJson["map"][j]
            j = j-1
        mapJson["map"][j+1] = curNode
    print("sorted: ",mapJson["map"])
    return mapJson

class Graph(object):
    def __init__(self, mapJson):
        self.pointsInfo = {}
        maxNodeNum = 100
        self.Infinity = 100000
        self.maxDeltaAngle = math.pi / 9
        self.firstInformDist = 200
        self.secondInformDist = 100
        self.maxDeltaDist = 20
        #http://wangwei007.blog.51cto.com/68019/1100742
        #mapJson["map"].sort(key = lambda x:x["nodeId"])
        #mapJson = sortNode(mapJson)
        self.nodeNum = len(mapJson["map"])
        #print(mapJson)
        for i in range(0, self.nodeNum):
            tempVertex = Vertex(mapJson["map"][i]["nodeName"],mapJson["map"][i]["x"],mapJson["map"][i]["y"])
            self.pointsInfo[int(mapJson["map"][i]["nodeId"])] = tempVertex 
        self.adjMatrix = [[self.Infinity for i in range(maxNodeNum)] for j in range(maxNodeNum)]
        #print(self.adjMatrix[1:self.nodeNum+1][1:self.nodeNum+1])
        #print("NodeNum is ",self.nodeNum)
        for i in range(0, self.nodeNum):
            self.adjMatrix[i+1][i+1] = 0       
            j = 0
            print("link is ",mapJson["map"][i]["linkTo"])
            linkList = mapJson["map"][i]["linkTo"].split()
            linkNum = len(linkList)
            print("linkNum is ",linkNum)
            for j in range(0,linkNum):
                id1 = i+1
                if linkList[j][len(linkList[j])-1] == ',':
                    temp = str(linkList[j])
                    id2 = int(temp[:len(linkList[j])-1])
                else: 
                    id2 = int(linkList[j])
                print(id1," ",id2)
                point1 = self.pointsInfo[id1]
                point2 = self.pointsInfo[id2]
                dis = Vertex.dist__(point1.x,point1.y,point2.x,point2.y)
                self.adjMatrix[id1][id2] = dis
    def __str__(self):
        print("There are %d nodes in sum. Their info is shown as below"%(self.nodeNum))
        for i in range(1, self.nodeNum+1):
            self.pointsInfo[i].__print__()
        #print("The adjacency matrix is shown as below")
        #for i in range(1, self.nodeNum+1):
            #print(self.adjMatrix[i][1:self.nodeNum+1])
    def CalAngle(x1,y1,x2,y2):
        temp = ( x1*x2 + y1*y2)/(math.sqrt(x1**2+y1**2)*math.sqrt(x2**2+y2**2))
        angle = math.acos(temp)
        rightforX = y1
        rightforY = -x1
        if ( rightforX*x2 + rightforY*y2)<0:
            angle = (-1)*angle
        return angle
    def __TurnInf__(self,angle):
        if angle>0:
            turnInf = "turn right for "+str(int(angle*180/math.pi))+" degrees "
        if angle==0:
            turnInf = "turn left for " + str(int(angle*180/math.pi)) + " degrees "
        if angle<0:
            turnInf = "go straight"
        return turnInf 
    def __Dijkstra__(self, startPoint, destPoint):
        prev = [-1 for i in range(self.nodeNum+2)]
        hasVisited = [0 for i in range(self.nodeNum+2)]
        dist = [self.Infinity for i in range(self.nodeNum+2)]
        dist[startPoint] = 0
        for i in range(1, self.nodeNum+1):
            if dist[i]!=self.Infinity:
                prev[i] = startPoint
        prev[startPoint] = 0
        for j in range(self.nodeNum):
            minDist = self.Infinity
            for i in range(1,self.nodeNum+1):
                if hasVisited[i]==0 and dist[i]<minDist:
                    minID = i
                    minDist = dist[i]
            hasVisited[minID] = 1 # mark minID has been visited     
            for i in range(1, self.nodeNum+1):
                if hasVisited[i]==0 and dist[minID]+self.adjMatrix[minID][i]<dist[i]:
                    dist[i] = dist[minID]+self.adjMatrix[minID][i]
                    prev[i] = minID
        route = []
        print("hasVisited: ",hasVisited)
        print("dist to startPoint is ", dist[1:self.nodeNum+1])
        print("previous point list is ",prev)
        tempNode = destPoint
        while prev[tempNode]!=0:
            route.append(tempNode)
            tempNode = prev[tempNode]
        route.append(startPoint)
        route.append(dist[destPoint])
        print(route)
        route.reverse()
        return route
    def __Navigate__(self,route):
        vel = 50
        deltaTime = 1
        for i in range(1,len(route)-1):
            curX = self.pointsInfo[route[i]].x
            curY = self.pointsInfo[route[i]].y
            nextDestX = self.pointsInfo[route[i+1]].x
            nextDestY = self.pointsInfo[route[i+1]].y
            angle = Vertex.angle__(self.pointsInfo[route[i]], self.pointsInfo[route[i+1]])
            nextVelX = vel * deltaTime * math.cos(angle)
            nextVelY = vel * deltaTime * math.sin(angle)
            velX = nextVelX
            velY = nextVelY
            Intruction = {""}
            while 1:
                print("U r now at (%d, %d)"%(curX,curY))
                if abs(Vertex.dist__(curX,curY,nextDestX,nextDestY)-self.firstInformDist)<self.maxDeltaDist:
                    print("Plz be prepared to",self. __TurnInf__(angle),self.firstInformDist," centimeters later")
                if abs(Vertex.dist__(curX,curY,nextDestX,nextDestY)-self.secondInformDist)<self.maxDeltaDist:
                    print("Plz be prepared to",self. __TurnInf__(angle),self.secondInformDist," centimeters later")
                nextX = curX + velX
                nextY = curY + velY
                if (nextX-nextDestX)*(nextDestX-curX)>0 or (nextY-nextDestY)*(nextDestY-curY)>0 or ( nextDestY == nextY and nextDestX == nextX) :
                    break
                curX = nextX
                curY = nextY
"""
print(Graph.CalAngle(2,2,1,1))
print(Graph.CalAngle(1,0,1,-1))
print(Graph.CalAngle(1,1,-1,-1))
"""
building = input("Plz input your building name: ")
level = input("Plz input your level: ")
with request.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building='+building+'&Level='+level) as f:
    data= f.read()
    #print('Data:', data.decode('utf-8'))
mapJson = json.loads(data.decode('utf-8'))
print("The number of nodes is %d"%(len(mapJson["map"])))

filename = str(input("Plz input your wanted filename: "))
with open(filename+".json",'w') as file:
    json.dump(mapJson,file)

graph = Graph(mapJson)
graph.__str__()
startPoint = int(input("Plz input your starting place: "))
destPoint = int(input("Plz input your destination: "))
route = graph.__Dijkstra__(startPoint, destPoint)


print(route)
print("The length of shortest path is", int(route[0]))
print("In detail, the route is ", route[1:len(route)+1])
graph.__Navigate__(route)

# data form: {"y": "350", "nodeName": "ap-104", "macAddr": "B1:44:A6:BB:EC:D0", "x": "500", "nodeId": "4"}

