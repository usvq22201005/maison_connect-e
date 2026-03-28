#include <DHTStable.h>

// ===== PINS =====
#define DHT_SALON 2
#define IR_PIN 3
#define DHT_CHAMBRE 4
#define SOUND_PIN A0

#define TRIG_PIN 22
#define ECHO_PIN 23

int buzzer = 8;
int relayPin = 9;

int ledChambre = 10;
int ledHeat = 11;
int ledSalon = 12;

int ledChambre2 = 6;
int ledHeat2 = 7;

DHTStable DHT;

// ===== VARIABLES =====
bool armed = false;
bool alarmTriggered = false;

unsigned long detectTime = 0;
const int delayBeforeAlarm = 3000;

void setup()
{
  Serial.begin(9600);

  pinMode(buzzer, OUTPUT);
  pinMode(IR_PIN, INPUT);

  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);

  pinMode(ledSalon, OUTPUT);
  pinMode(ledChambre, OUTPUT);
  pinMode(ledHeat, OUTPUT);

  pinMode(ledChambre2, OUTPUT);
  pinMode(ledHeat2, OUTPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

// ===== DISTANCE =====
long getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  long distance = duration * 0.034 / 2;

  return distance;
}

void loop()
{
  // ===== COMMANDES =====
  if (Serial.available())
  {
    char cmd = Serial.read();

    if (cmd == 'S') digitalWrite(ledSalon, HIGH);
    if (cmd == 's') digitalWrite(ledSalon, LOW);

    if (cmd == 'L') digitalWrite(ledChambre, HIGH);
    if (cmd == 'l') digitalWrite(ledChambre, LOW);

    if (cmd == 'H') digitalWrite(ledHeat, HIGH);
    if (cmd == 'h') digitalWrite(ledHeat, LOW);

    if (cmd == 'R') digitalWrite(relayPin, LOW);
    if (cmd == 'r') digitalWrite(relayPin, HIGH);

    if (cmd == 'K') digitalWrite(ledChambre2, HIGH);
    if (cmd == 'k') digitalWrite(ledChambre2, LOW);

    if (cmd == 'J') digitalWrite(ledHeat2, HIGH);
    if (cmd == 'j') digitalWrite(ledHeat2, LOW);

    if (cmd == 'A') armed = true;
    if (cmd == 'a') {
      armed = false;
      alarmTriggered = false;
      noTone(buzzer);
    }
  }

  // ===== IR =====
  int detect = digitalRead(IR_PIN);

  if (armed)
  {
    if (detect == LOW)
    {
      if (detectTime == 0) detectTime = millis();
      if (millis() - detectTime > delayBeforeAlarm)
      {
        alarmTriggered = true;
      }
    }
    else detectTime = 0;
  }

  // ===== DHT SALON =====
  int chkS = DHT.read11(DHT_SALON);

  if (chkS == DHTLIB_OK)
  {
    Serial.print("S:");
    Serial.print(DHT.getTemperature());
    Serial.print(",");
    Serial.print(DHT.getHumidity());
    Serial.print(";");
  }

  // ===== DHT CHAMBRE =====
  int chkC = DHT.read11(DHT_CHAMBRE);

  if (chkC == DHTLIB_OK)
  {
    Serial.print("C:");
    Serial.print(DHT.getTemperature());
    Serial.print(",");
    Serial.print(DHT.getHumidity());
    Serial.print(";");
  }

  // ===== SON =====
  int total = 0;
  for(int i=0; i<10; i++) {
    total += analogRead(SOUND_PIN);
    delay(5);
  }
  int soundLevel = total / 10;

  Serial.print("N:");
  Serial.print(soundLevel);
  Serial.print(";");

  // ===== GARAGE =====
  long distance = getDistance();

  Serial.print("G:");
  Serial.println(distance);

  // ===== ALARME =====
  if (alarmTriggered)
  {
    for(int f=800; f<1200; f+=50)
    {
      tone(buzzer,f);
      delay(20);
    }
    for(int f=1200; f>800; f-=50)
    {
      tone(buzzer,f);
      delay(20);
    }
  }
  else noTone(buzzer);

  delay(1000);
}