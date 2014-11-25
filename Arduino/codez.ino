const int ledPin = 13;
const int piezo = A0;

void setup()
{
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop()
{
  Serial.println(analogRead(piezo));
  if (Serial.available())
  {
     flash(Serial.read() - '0');
  }
  delay(1000);
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

