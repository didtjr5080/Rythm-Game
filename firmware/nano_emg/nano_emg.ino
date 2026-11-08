// Classic Arduino Nano / ATmega328P. EMG module analog output -> A0.
// 500 Hz ADC sampling, 50 Hz framed USB serial output at 115200 baud.
const uint8_t EMG_PIN = A0;
const uint32_t SAMPLE_US = 2000;
const uint32_t OUTPUT_US = 20000;
float baseline = 0;
float envelope = 0;
uint16_t rawValue = 0;
uint16_t calibrationSamples = 0;
uint32_t sequence = 0;
uint32_t lastSample = 0;
uint32_t lastOutput = 0;
uint32_t lastIdentity = 0;
char command[16];
uint8_t commandLength = 0;

void identify() {
  Serial.println(F("EMG_DEVICE:NANO_A0:1"));
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(EMG_PIN, INPUT);
  Serial.begin(115200);
  baseline = analogRead(EMG_PIN);
  identify();
}

void loop() {
  while (Serial.available()) {
    const char c = Serial.read();
    if (c == '\n') {
      command[commandLength] = '\0';
      if (strcmp(command, "EMG?") == 0) identify();
      if (strcmp(command, "ZERO") == 0) {
        calibrationSamples = 0;
        envelope = 0;
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
    lastSample = now;
    rawValue = analogRead(EMG_PIN);
    if (calibrationSamples < 250) {
      calibrationSamples++;
      baseline += (rawValue - baseline) / calibrationSamples;
      envelope = 0;
    } else {
      // Remove DC offset for a raw bipolar EMG output, then rectify/smooth.
      // For sensor modules with their own ENV output, select RAW A0 in the app.
      baseline += 0.001f * (rawValue - baseline);
      const float magnitude = fabs(rawValue - baseline);
      envelope += 0.08f * (magnitude - envelope);
    }
  }
  if ((uint32_t)(now - lastOutput) >= OUTPUT_US) {
    lastOutput = now;
    Serial.print(F("EMG1 raw:"));
    Serial.print(rawValue);
    Serial.print(F(" filtered:"));
    Serial.print((uint16_t)constrain(envelope, 0.0f, 1023.0f));
    Serial.print(F(" seq:"));
    Serial.println(sequence++);
  }
  digitalWrite(LED_BUILTIN, envelope >= 40 || millis() % 1000 < 80);
}
