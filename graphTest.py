
import json
import math
from urllib import request
from vertexTest import *   


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
            linkList = mapJson["map"][i]["linkTo"].split(", ")
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
                dis = Vertex.dist__(point1.x,point1.y,point2.x,point2.y)
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
    		turnInf = "turn right for "+str(int(angle*180/math.pi))+" degrees "
    	elif angle < (-1)*self.maxDeltaAngle:
    		turnInf = "turn left for " + str(int(-angle*180/math.pi)) + " degrees "
    	else:
    		turnInf = "go straight"
    	return turnInf 

    #To calculate the shortest route using dijkstra
    def __Dijkstra__(self, startPoint, destPoint):

    	#initiate
        prev = [-1 for i in range(self.nodeNum+2)]				#prev[i] means the previous point before visiting i 
        hasVisited = [0 for i in range(self.nodeNum+2)]			#hasVisited[i] means whether point i has been visited
        dist = [self.Infinity for i in range(self.nodeNum+2)]	#dist[i] means the shortest distance between i and star tPoint
        dist[startPoint] = 0
        for i in range(1, self.nodeNum+1):
            if dist[i]!=self.Infinity:
                prev[i] = startPoint
        prev[startPoint] = 0

        #dijkstra
        for j in range(self.nodeNum):
            minDist = self.Infinity
            for i in range(1,self.nodeNum+1):					#find the min distance
                if hasVisited[i]==0 and dist[i]<minDist:
                    minID = i
                    minDist = dist[i]
            hasVisited[minID] = 1 								# mark minID has been visited     
            for i in range(1, self.nodeNum+1):					# update
                if hasVisited[i]==0 and dist[minID]+self.adjMatrix[minID][i]<dist[i]:
                    dist[i] = dist[minID]+self.adjMatrix[minID][i]
                    prev[i] = minID
        route = []
        if (debug):
        	print("hasVisited: ",hasVisited)
        	print("dist to startPoint is ", dist[1:self.nodeNum+1])
        	print("previous point list is ",prev)
        tempNode = destPoint
        while prev[tempNode]!=0:								#transform prev[] to route[]
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
    	userPos =  [{"x":400,"y":200,"heading":0}, {"x":500,"y":200,"heading":90},{"x":595,"y":200,"heading":90},
    	{"x":600,"y":300,"heading":0},{"x":600,"y":486,"heading":10}]
    	curRouteId = 1
    	nextRouteId = curRouteId+1
    	totalRoute = len(route)-1
    	posId = 0
    	
    	while 1>0:
    		curX = userPos[posId]["x"] 
    		curY = userPos[posId]["y"] 
    		curDist = Vertex.dist__(curX, curY, self.pointsInfo[route[nextRouteId]].x, self.pointsInfo[route[nextRouteId]].y)
    		#check whether the user has reached next destination
    		if (curDist<self.maxDeltaDist):
    			print("Congratulations! You have reached ", self.pointsInfo[route[nextRouteId]].name, "! ")
    			curRouteId = nextRouteId
    			if (curRouteId == totalRoute):
    				print("This is your destination. Please stop now.")
    				break
    			nextRouteId = nextRouteId + 1
    			curDist = Vertex.dist__(curX, curY, self.pointsInfo[route[nextRouteId]].x, self.pointsInfo[route[nextRouteId]].y)
    		#calculate turning angle
    		curAngle = Graph.TransformAngle(userPos[posId]["heading"])
    		tempVertex = Vertex("temp",curX, curY)
    		aimedAngle = Vertex.angle__(tempVertex, self.pointsInfo[route[nextRouteId]]) / math.pi * 180
    		turningAngle = (curAngle - aimedAngle) % 360
    		if abs(turningAngle)>180:
    			if turningAngle>0:
    				turningAngle = turningAngle - 360
    			else:
    				turningAngle = 360 + turningAngle
    		print(turningAngle," ",curDist)
    		posId = posId + 1


#Download the map
building = input("Plz input your building name: ")
level = input("Plz input your level: ")
with request.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building='+building+'&Level='+level) as f:
    data= f.read()
mapJson = json.loads(data.decode('utf-8'))
print("The number of nodes is %d"%(len(mapJson["map"])))
print("The name of the first node is", mapJson["map"][0]["nodeName"])

#save tge json file
filename = str(input("Plz input your wanted filename: "))
with open(filename+".json",'w') as file:
    json.dump(mapJson,file)

#get the shortest path and navigate
graph = Graph(mapJson)
if debug:
	graph.__str__()
startPoint = int(input("Plz input your starting place: "))
destPoint = int(input("Plz input your destination: "))
route = graph.__Dijkstra__(startPoint, destPoint)
graph.__SoosNavigate__(route)



