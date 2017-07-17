import json
from urllib import request
building = input("Plz input your building name: ")
level = input("Plz input your level: ")
with request.urlopen('http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building='+building+'&Level='+lev) as f:
	data= f.read()
	print('Data:', data.decode('utf-8'))
mapJson = json.loads(data.decode('utf-8'))
print(mapJson)
#j_str = json.dumps(mapJson)
#print("jstr is %s"%(j_str))
print("The number of nodes is %d"%(len(mapJson["map"])))

filename = str(input("Plz input your wanted filename: "))
with open(filename+".json",'w') as file:
	json.dump(mapJson,file)

with open("c:\a.txt",'r') as filename:
	contents = filename.read()