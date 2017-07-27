import os, sys

pwd = sys.path[0]
if os.path.isfile(pwd):
    pwd = os.path.dirname(pwd)
print("pwd: ",pwd)
#building = str(input("Plz input your building name: "))
#level = str(input("Plz input your level: "))
building = str(ReadNum("Plz input your building name: "))
level = str(ReadNum("Plz input your level: "))
print(pwd + "/map/" + building + "_" + level +".json")
with open(pwd + "/map/" + building + "_" + level +".json",'r') as filename:
    contents = filename.read()
mapJson = json.loads(contents)
print("mapJson: ",mapJson)