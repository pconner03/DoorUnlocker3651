import sqlite3
import getpass
import hashlib #sqlite has no hash functions
import serial
import common

ser = serial.Serial(common.TTY, 9600)

con = sqlite3.connect("doorlock.db")

#check if table exists already
cur = con.cursor()
try:
	cur.execute("CREATE TABLE users(number TEXT PRIMARY KEY, passwordHash TEXT, knockPattern TEXT)")
	print "Creating users table..."
except:
	print "Found users table"

while True:
	rawNum = raw_input("Enter phone number: ")

	cleanNum = ''.join([c for c in rawNum if c >= "0" and c <= "9"])

	if len(cleanNum) == 10:
		cleanNum = "1"+cleanNum
	if len(cleanNum) != 11 or cleanNum[0] != '1':
		print "Invalid phone number format"
		continue
	twilioNum = "+" + cleanNum
	break
#TODO - check if user already exists
while True:
	pwd = getpass.getpass("Enter password: ")
	pwd2 = getpass.getpass("Confirm password: ")
	if pwd != pwd2:
		print "Error. Passwords do not match"
		continue
	break

while True:
	ser.write(common.LISTEN_COMMAND)
	print "Perform secret knock"
	arrayString = ser.readline()
	distanceArray = [int(i) for i in arrayString.split(",")[:-1] if i != "0"]
	if len(distanceArray) == 0:
		print "Knock Timed Out. Please Retry"
	else:
		distanceArray = common.convertToRatio(distanceArray)
		toStr = common.toKnockString(distanceArray)
		ser.write(common.LISTEN_COMMAND)
		print "Confirm secret knock"
		#print "Knock string: " + toStr
		#confirmStr = raw_input("Accept knock string? (y/n)")
		#if confirmStr.lower() in ("yes", "y"):
		#	break
		arrayString = ser.readline()
		distanceArray = [int(i) for i in arrayString.split(",")[:-1] if i != "0"]
		if len(distanceArray) == 0:
			print "Knock Timed Out. Please Retry"
			continue
		else:
			distanceArray = common.convertToRatio(distanceArray)
			secondStr = common.toKnockString(distanceArray)
			if secondStr != toStr:
				print "Knocks do not match. Please retry when prompted"
				continue
			else:
				print "Knock accepted"
				break


print "Attempting to insert into database"

insQ = "INSERT INTO users(number, passwordHash, knockPattern) VALUES ('" + twilioNum+"', '" + hashlib.sha256(pwd).hexdigest()+"', '"+toStr+"');"
cur.execute(insQ)
con.commit()
con.close()

print "User added succesfully"
