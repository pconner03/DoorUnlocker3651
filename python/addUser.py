import sqlite
import getpass
import hashlib #sqlite has no hash functions
con = sqlite.connect("doorlock.db")

#check if table exists already
cur = con.cursor()
try:
	cur.execute("CREATE TABLE users(number TEXT PRIMARY KEY, passwordHash TEXT)")
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

insQ = "INSERT INTO users(number, passwordHash) VALUES ('" + twilioNum+"', '" + hashlib.sha256(pwd).hexdigest()+"');"
cur.execute(insQ)
con.commit()
con.close()
