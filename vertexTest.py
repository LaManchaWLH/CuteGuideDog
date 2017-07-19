import math
class Vertex(object):  
    def __init__(self, name, x, y):
        self.name = name
        self.x = float(x)
        self.y = float(y)
    def __str__(self):
        res = str(self.name) + "(" + str(self.x) + "," + str(self.y)+")"
        return res
    def __print__(self):
        res = str(self.name) + "(" + str(self.x) + "," + str(self.y)+")"
        print("%s"%(res))
    def dist__(x1,y1,x2,y2):
        dist = math.sqrt(((x1-x2)**2+(y1-y2)**2)*1.0)
        return dist
    def angle__(point1, point2):
        if point2.x == point1.x:
            angle = math.pi/2
        else:
            angle = math.atan((point1.y-point2.y)*1.0/(point1.x-point2.x))
        if point2.y<point1.y:
            angle = angle + math.pi
        return angle
    #Add other methods below


#Sample test of basic functionalities given
#v1 = Vertex("A", 100, 200)
#print(v1)
