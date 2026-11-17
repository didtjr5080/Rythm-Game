// ESP8266EX / NodeMCU: EMG analog output -> A0 (NOT D0 / GPIO16).
// Verify the development board ADC input voltage limit before wiring.
#include <ESP8266WiFi.h>
#include "szh_gjd001_filter.h"
// 500 Hz ADC sampling, 50 Hz framed USB serial output at 115200 baud.
const uint8_t EMG_PIN = A0;
const uint32_t SAMPLE_US = 2000;
const uint32_t OUTPUT_US = 20000;
SzhGjd001Filter signalFilter;
SzhGjd001Filter noBandpassFilter(false);
float envelope = 0;
float noBandpassRms = 0;
uint16_t rawValue = 0;
uint32_t sequence = 0;
uint32_t lastSample = 0;
uint32_t lastOutput = 0;
uint32_t lastIdentity = 0;
char command[16];
uint8_t commandLength = 0;

void identify() {
  Serial.println(F("EMG_DEVICE:ESP8266_A0:2"));
}

void setup() {
  WiFi.persistent(false);
  WiFi.mode(WIFI_OFF);
  pinMode(LED_BUILTIN, OUTPUT);
  // A0 is the dedicated ADC input, not a digital GPIO.
  Serial.begin(115200);
  identify();
}

void loop() {
  while (Serial.available()) {
    const char c = Serial.read();
    if (c == '\n') {
      command[commandLength] = '\0';
      if (strcmp(command, "EMG?") == 0) identify();
      if (strcmp(command, "ZERO") == 0) {
        signalFilter.reset();
        noBandpassFilter.reset();
        envelope = 0;
        noBandpassRms = 0;
      }
      commandLength = 0;
    } else if (c != '\r') {
      if (commandLength < sizeof(command) - 1) command[commandLength++] = c;
      else commandLength = 0;
    }
  }
  if ((uint32_t)(millis() - lastIdentity) >= 1000) {
    lastIdentity = millis();
    identify();
  }
  const uint32_t now = micros();
  if ((uint32_t)(now - lastSample) >= SAMPLE_US) {
    lastSample += SAMPLE_US;
    if ((uint32_t)(now-lastSample) >= SAMPLE_US) {
      // A missed period invalidates the fixed-rate filter history; never invent samples.
      lastSample = now;
      signalFilter.reset();
      noBandpassFilter.reset();
    }
    rawValue = analogRead(EMG_PIN);
    envelope = signalFilter.update(rawValue);
    noBandpassRms = noBandpassFilter.update(rawValue);
  }
  if ((uint32_t)(now - lastOutput) >= OUTPUT_US) {
    lastOutput = now;
    Serial.print(F("EMG1 raw:"));
    Serial.print(rawValue);
    Serial.print(F(" filtered:"));
    Serial.print((uint16_t)constrain(envelope, 0.0f, 1023.0f));
    Serial.print(F(" seq:"));
    Serial.println(sequence);
    // Extension starts with EMG1 so older app readers safely ignore this line.
    Serial.print(F("EMG1_BYPASS rms:"));
    Serial.print((uint16_t)constrain(noBandpassRms, 0.0f, 1023.0f));
    Serial.print(F(" seq:"));
    Serial.println(sequence++);
  }
  digitalWrite(LED_BUILTIN, (envelope >= 40 || millis() % 1000 < 80) ? LOW : HIGH);
  yield();
}
