import serial
import syslog,time,sys
ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)

#ser.write("testing serial connection\n".encode('utf-8'))
#ser.write("sending via RPi\n".encode('utf-8'))
'''
ACK = '0x11'
Hello = '0x12'
RIGHT = '0x13'
'''
ACK = bytearray()
ACK.extend(bytes([0x11]))
HELLO = bytearray()
HELLO.extend(bytes([0x12]))
RIGHT = bytearray()
RIGHT.extend(bytes([0x13]))
print(HELLO)
flagACK = 0
#ser.write("lala")
while 1:
	ser.write(HELLO)
	print("sending: ",HELLO)
	time.sleep(0.2)
	response = ser.read()
	print("receiving: ",response)
	#print "receiving: "+response
	if response == ACK:
		print("success of received ACK")
		break
	time.sleep(0.2)

while 1:
	ser.write(ACK)
	time.sleep(0.2)
	response = ser.read()
	if response == RIGHT:
		print("Final SUCCESS! hhh :)")
		break

try:
	while 1:
		response = ser.read()
		print( "Msg from Arduino: ",response)
		"""
		if response==RIGHT:
			break
		if response==ACK:
			flagACK = 1
		
		if flagACK>0:
			ser.write(ACK)
			print "Is sending ACK" 
		else:
			ser.write(HELLO)
			print "Is sending Hello"
		"""
		time.sleep(0.3)

except KeyboardInterrupt:
	ser.close()

