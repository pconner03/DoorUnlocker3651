'''
Hack to get around Twilio's suggested method for receiving messages
'''

from twilio.rest import TwilioRestClient as TRC
import credentials #local file. requires two string variables: account_sid and auth_token
#import daemon #TODO  
import sqlite3
import time
import datetime
from email.utils import parsedate
import hashlib
import serial

twilioNumber = ""
client = None

LISTEN_COMMAND = str(1)
UNLOCK_COMMAND = str(2)

SHORT_RANGE = (0,33)
MEDIUM_RANGE = (34, 66)
LONG_RANGE = (67, 100)

SHORT = "0"
MEDIUM = "1"
LONG = "2"
'''
0 is short
1 is medium
2 is long
'''

TEST_KNOCK = "100121"


ser = serial.Serial('/dev/ttyACM0', 9600)


def main():
	global twilioNumber
	global client
	TIME_TO_SLEEP = 5.0 #poll every 5 seconds
	client = TRC(credentials.account_sid, credentials.auth_token)

	twilioNumber = client.phone_numbers.list()[0].phone_number

	lastTimeChecked = datetime.datetime.now().timetuple()
	#TODO - turn into a daemon
	while True:
		newtime = None
		for m in client.messages.list():
			if m.from_ != twilioNumber: #ignore messages we sent
				mTime = parsedate(m.date_sent)
				if mTime > lastTimeChecked:
					if not newtime:
						newtime = mTime #new most recent message

					parseText(m.from_, m.body)	

				else:
					break
		if newtime:
			lastTimeChecked = newtime

		time.sleep(TIME_TO_SLEEP)

def parseText(num, password):
	global twilioNumber
	global UNLOCK_COMMAND
	global LISTEN_COMMAND
	global ser
	con = sqlite3.connect("doorlock.db")
	cur = con.cursor()
	query = "SELECT passwordHash FROM users WHERE number='" + num+ "';"
	cur.execute(query)
	result = cur.fetchone()
	if not result: #is this the way fetchone works??
		print "Unknown user attempt"
	else:
		if hashlib.sha256(password).hexdigest() == result[0]:
			print "Valid attempt!!!"
			
			angle = 0
			confirmMessage = client.messages.create(to=num, from_=twilioNumber,body="Valid password. Start knocking!" )
			ser.write(LISTEN_COMMAND)
			arrayString = ser.readline()
			print "Got string " + arrayString
			distanceArray = [int(i) for i in arrayString.split(",")[:-1] if i != "0"]
			if len(distanceArray) == 0:
				print "Knock timed out"
				return
			distanceArray = convertToRatio(distanceArray)
			print "Distance percentages"
			print distanceArray			

			secretKnock = TEST_KNOCK #TODO - get from database
			if len(distanceArray) != len(secretKnock):
				print "Incorrect knock (length)"
				return
			for i in range(len(distanceArray)):
				if not inRange(secretKnock[i], distanceArray[i]):
					print "Incorrect knock (sequence)"
			print "Correct knock!"
			ser.write(UNLOCK_COMMAND)

		else:
			print "Invalid attempt by known user"

def convertToRatio(distanceArray):
	mx = distanceArray[0]
	for i in distanceArray:
		if i > mx:
			mx = i
	for i in range(len(distanceArray)):
		distanceArray[i] = int((float(distanceArray[i])/mx) * 100)
	return distanceArray


def inRange(type, percent):
	if type == SHORT:
		tup = SHORT_RANGE
	elif type == MEDIUM:
		tup = MEDIUM_RANGE
	else:
		tup = LONG_RANGE
	return percent >= tup[0] and percent <= tup[1]

main()