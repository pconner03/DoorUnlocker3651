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


import common

twilioNumber = ""
client = None

TEST_KNOCK = "100121"


ser = serial.Serial(common.TTY, 9600)


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
	global ser
	con = sqlite3.connect("doorlock.db")
	cur = con.cursor()
	query = "SELECT passwordHash, knockPattern FROM users WHERE number='" + num+ "';"
	cur.execute(query)
	result = cur.fetchone()
	if not result: #is this the way fetchone works??
		print "Unknown user attempt"
	else:
		if hashlib.sha256(password).hexdigest() == result[0]:
			secretKnock = result[1]
			print "Valid attempt!!!"
			
			angle = 0
			confirmMessage = client.messages.create(to=num, from_=twilioNumber,body="Valid password. Start knocking!" )
			ser.write(common.LISTEN_COMMAND)
			arrayString = ser.readline()
			print "Got string " + arrayString
			distanceArray = [int(i) for i in arrayString.split(",")[:-1] if i != "0"]
			if len(distanceArray) == 0:
				print "Knock timed out"
				return
			distanceArray = common.convertToRatio(distanceArray)
			print "Distance percentages"
			print distanceArray			

			#secretKnock = TEST_KNOCK #TODO - get from database - DONE
			if len(distanceArray) != len(secretKnock):
				print "Incorrect knock (length)"
				return
			compareString = common.toKnockString(distanceArray)
			if compareString != secretKnock:
					print "Incorrect knock (sequence)"
					return
			print "Correct knock!"
			ser.write(common.UNLOCK_COMMAND)

		else:
			print "Invalid attempt by known user"


main()