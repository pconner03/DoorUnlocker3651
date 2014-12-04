#include <Servo.h>

Servo myServo;

const int ledPin = 13;
const int piezo = A1;
const int servoPin = 9;
int pos = 0;

const int knockThreshold = 400;
const int timeout = 2000;

void setup()
{
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  myServo.attach(servoPin);
}

void loop()
{
  waitForSerial();
//  Serial.println(analogRead(piezo));
//  if (Serial.available())
//  {
//     // flash(Serial.read() - '0');
//     myServo.write(Serial.read());
//  }
//  delay(1000);
}

void flash(int n)
{
  for (int i = 0; i < n; i++)
  {
    digitalWrite(ledPin, HIGH);
    delay(100);
    digitalWrite(ledPin, LOW);
    delay(100);
  }
}

void waitForSerial() {
  if(Serial.available()){
    int val = Serial.read() - '0';
    if(val == 1) {
      flash(10);
      listenForKnocks();
    } else if(val == 2) {
      unlock();
    } else if(val == 3) {
      lock();
    }
  }
  delay(100);
}

void listenForKnocks() {
  int knockIntervals[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  int index = 0;
  unsigned long timerStart = millis();
  int timerEnd = 0;
  while(analogRead(piezo) > knockThreshold) {
    //TODO - check for long timeout
  }
  boolean isKnock = true;
  timerStart = millis();
  while(millis() - timerStart < timeout && index < 12) {
//  while(true) {
    int piezoVal = analogRead(piezo);
    if(!isKnock && (piezoVal < knockThreshold)) {
      knockIntervals[index] = millis() - timerStart;
      isKnock = true;
      index++;
      delay(10);
    } else if(piezoVal >= knockThreshold && isKnock) {
      timerStart = millis();
      isKnock = false;
      delay(10);
    }
  }
  String knockArray = "";
  for(index = 0; index < 12; index++) {
//    if(knockIntervals[index] == 0) break;
    knockArray += knockIntervals[index];
    knockArray += ",";
  }
  Serial.println(knockArray);
}

void lock()
{
  if (myServo.read() < 60) {
    for (pos = 50; pos < 160; pos += 1)
    {
      myServo.write(pos);
      delay(15);
    }
  }
}
 
void unlock()
{
  if (myServo.read() > 60) {
    for(pos = 160; pos>=50; pos -= 1)     // goes from 150 degrees to 50 degrees
    {                                
      myServo.write(pos);              // tell servo to go to position in variable 'pos'
      delay(15);                       // waits 15ms for the servo to reach the position
    }
  }
}

