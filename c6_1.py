n = raw_input("Plz input a number: ")
n = int(n)
for i in range(1,n+1):
	if i%15==0:
		print("%dFizzBuzz"%(i))
	elif i%5==0:
		print("%dBuzz"%(i))
	elif i%3==0:
		print("%dFizz"%(i))
	else:
		print("%d"%(i))