from twilio.rest import TwilioRestClient as TRC
import credentials

client = TRC(credentials.account_sid, credentials.auth_token)

myNumber = client.phone_numbers.list()[0].phone_number
for m in client.messages.list():
	if m.from_ != myNumber:
		print "From : " + m.from_ +" at "+m.date_sent
		print m.body
		print "-----"
