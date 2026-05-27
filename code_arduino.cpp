#include <DHTStable.h>

// ===== PINS =====
#define DHT_SALON 2
#define IR_PIN 3
#define DHT_CHAMBRE 4
#define SOUND_PIN 50
#define TRIG_PIN 22
#define ECHO_PIN 23

int buzzer = 8;
int relayPin = 9;
int ledChambre = 10;
int ledHeat = 11;
int ledSalon = 12;
int ledChambre2 = 6;
int ledHeat2 = 7;
int garageLed_R = 26;
int garageLed_V = 24;

DHTStable DHT;

// ===== VARIABLES =====
bool armed = false;
bool alarmTriggered = false;
unsigned long detectTime = 0;
const int delayBeforeAlarm = 1000;
long seuil_garage = 10;

// Variables pour remplacer le delay() bloquant
unsigned long lastSlowCheck = 0;
const unsigned long slowInterval = 1000; // 1 seconde pour le bloc lourd

void setup() {
  Serial.begin(9600);
  pinMode(buzzer, OUTPUT);
  pinMode(IR_PIN, INPUT);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  pinMode(ledSalon, OUTPUT);
  pinMode(ledChambre, OUTPUT);
  pinMode(ledHeat, OUTPUT);
  pinMode(ledChambre2, OUTPUT);
  pinMode(ledHeat2, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(garageLed_R, OUTPUT);
  pinMode(garageLed_V, OUTPUT);
  pinMode(SOUND_PIN, INPUT_PULLUP);
}

long getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // Timeout pour éviter de figer
  return duration * 0.034 / 2;
}

void loop() {
  // ===== 1. COMMANDES SÉRIE (Instantané) =====
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'S') digitalWrite(ledSalon, HIGH);
    if (cmd == 's') digitalWrite(ledSalon, LOW);
    if (cmd == 'L') digitalWrite(ledChambre, HIGH);
    if (cmd == 'l') digitalWrite(ledChambre, LOW);
    if (cmd == 'H') digitalWrite(ledHeat, HIGH);
    if (cmd == 'h') digitalWrite(ledHeat, LOW);
    if (cmd == 'R') digitalWrite(relayPin, HIGH);
    if (cmd == 'r') digitalWrite(relayPin, LOW);
    if (cmd == 'K') digitalWrite(ledChambre2, HIGH);
    if (cmd == 'k') digitalWrite(ledChambre2, LOW);
    if (cmd == 'J') digitalWrite(ledHeat2, HIGH);
    if (cmd == 'j') digitalWrite(ledHeat2, LOW);
    if (cmd == 'A') armed = true;
    if (cmd == 'a') {
      armed = false;
      alarmTriggered = false;
      Serial.print("A:0;");
      noTone(buzzer);
    }
    if (cmd == 'T') {
      String value = Serial.readStringUntil('\n');
      seuil_garage = value.toInt();
    }
  }


  // ===== 2. ENVOI DONNEES CAPTEURS (Toutes les 1 seconde, sans bloquer) =====
  unsigned long currentMillis = millis();
  if (currentMillis - lastSlowCheck >= slowInterval) {
    lastSlowCheck = currentMillis;

    // INTRUSION IR
    int detect = digitalRead(IR_PIN);
    if (armed) {
      if (detect == LOW) {
        if (detectTime == 0) detectTime = millis();
        if (millis() - detectTime > delayBeforeAlarm) {
          alarmTriggered = true;
          Serial.print("A:1;");
        }
      } else {
        detectTime = 0;
      }
    }

    // DHT SALON
    if (DHT.read11(DHT_SALON) == DHTLIB_OK) {
      Serial.print("S:"); Serial.print(DHT.getTemperature());
      Serial.print(","); Serial.print(DHT.getHumidity()); Serial.print(";");
    }

    // DHT CHAMBRE
    if (DHT.read22(DHT_CHAMBRE) == DHTLIB_OK) {
      Serial.print("C:"); Serial.print(DHT.getTemperature());
      Serial.print(","); Serial.print(DHT.getHumidity()); Serial.print(";");
    }

    // SON CHAMBRE
    if (digitalRead(SOUND_PIN) == LOW) {
      delayMicroseconds(20); // Laisse passer le pic de parasite induit par l'ultrason
      if (digitalRead(SOUND_PIN) == LOW) {
        Serial.print("N:0;");
      } else {
        Serial.print("N:1;");
      }
    } else {
      Serial.print("N:1;");
    }

    // GARAGE
    long distance = getDistance();
    if (distance <= seuil_garage) {
      digitalWrite(garageLed_R, HIGH); digitalWrite(garageLed_V, LOW);
    } else {
      digitalWrite(garageLed_R, LOW); digitalWrite(garageLed_V, HIGH);
    }
    Serial.print("G:"); Serial.print(distance); Serial.println(";");
  }

  // ===== 4. ALARME SORENTE =====
  if (alarmTriggered) {
    tone(buzzer, 1000); // Signal fixe plus rapide que les boucles for complexes
  } else {
    noTone(buzzer);
  }
}