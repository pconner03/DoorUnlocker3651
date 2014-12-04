LISTEN_COMMAND = str(1)
UNLOCK_COMMAND = str(2)
LOCK_COMMAND = str(3)

SHORT_RANGE = (0,33)
MEDIUM_RANGE = (34, 66)
LONG_RANGE = (67, 100)

SHORT = "0"
MEDIUM = "1"
LONG = "2"

TTY = "/dev/ttyACM0"


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
