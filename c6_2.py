phonebook = {"James":12345, "Bond":77777}
for i in range(1,100):
	print("Here is your options: 1-Add/Edit phonebook 2-Look up phonebook 3-Quit")
	option = input("Plz input your option ID: ")
	option = int(option)
	if option == 1:
		name = raw_input("Plz input the user name: ")
		num = raw_input("Plz input your phone number: ")
		phonebook[str(name)]= int(num)
	if option == 2:
		name = raw_input("Plz input the user name: ")
		print("The phonenumber is %s"%(phonebook[str(name)]))
	if option == 3:
		break

