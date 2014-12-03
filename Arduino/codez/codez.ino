#include <Servo.h>

Servo myServo;

const int ledPin = 13;
const int piezo = A0;
const int servoPin = 9;

const int knockThreshold = 200;
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
    Serial.println(val);
    if(val == 1) {
      listenForKnocks();
    } else if(val == 2) {
      unlock();
    }
  }
  delay(100);
}

void listenForKnocks() {
  int knockIntervals[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  int index = 0;
  unsigned long timerStart = millis();
  int timerEnd = 0;
  Serial.print("I'm listening");
  while(analogRead(piezo) < knockThreshold) {
    //TODO - check for long timeout
  }
  Serial.println("Got past the long timeout");
  boolean isKnock = true;
  timerStart = millis();
  while(millis() - timerStart < timeout && index < 12) {
    int piezoVal = analogRead(piezo);
    if(!isKnock && (piezoVal > knockThreshold)) {
      knockIntervals[index] = millis() - timerStart;
      isKnock = true;
      index++;
      Serial.println(index);
      delay(10);
    } else if(piezoVal <= knockThreshold && isKnock) {
      timerStart = millis();
      isKnock = false;
      delay(10);
    }
  }
  Serial.println("Finished looping");
  String knockArray = "";
  for(index = 0; index < 12; index++) {
//    if(knockIntervals[index] == 0) break;
    knockArray += knockIntervals[index];
    knockArray += ",";
  }
  Serial.println(knockArray);
}

void unlock() {
  myServo.write(135);
}
