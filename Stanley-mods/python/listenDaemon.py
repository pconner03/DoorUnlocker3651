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



def main():
	TIME_TO_SLEEP = 25.0 #poll every 25 seconds
	client = TRC(credentials.account_sid, credentials.auth_token)

	twilioNumber = client.phone_numbers.list()[0].phone_number

	lastTimeChecked = datetime.datetime.now().timetuple()
	#TODO - turn into a daemon
	while True:
		newtime = None
		for m in client.messages.list(date_sent = datetime.date.today()):
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
			ser = serial.Serial('/dev/ttyACM1', 9600)
			while 1:
				ser.write('1')
				print ser.readline()
		else:
			print "Invalid attempt by known user"

main()