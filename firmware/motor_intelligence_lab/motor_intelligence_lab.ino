#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// Example pins for a classic ESP32 DevKit; verify for your board.
static constexpr int CURRENT_ADC_PIN = 34;
static constexpr int I2C_SDA_PIN = 21;
static constexpr int I2C_SCL_PIN = 22;

// Calibrate these using the exact sensor module and any voltage divider.
// Values are referred to the ESP32 ADC input, unless otherwise stated.
static constexpr float CURRENT_ZERO_V = 1.65f;
static constexpr float CURRENT_SENSITIVITY_V_PER_A = 0.100f;
static constexpr float ADC_DIVIDER_RATIO = 1.0f; // sensor output / ADC-pin voltage
static constexpr uint32_t SAMPLE_PERIOD_MS = 20;

Adafruit_MPU6050 mpu;
bool capturing = false;
uint32_t startMs = 0;
uint32_t lastSampleMs = 0;

float readCurrentA(int &rawOut) {
  rawOut = analogRead(CURRENT_ADC_PIN);
  // Approximation only: ESP32 ADC response varies by chip, attenuation and board.
  const float vAdc = (static_cast<float>(rawOut) / 4095.0f) * 3.3f;
  const float vSensor = vAdc * ADC_DIVIDER_RATIO;
  return (vSensor - CURRENT_ZERO_V) / CURRENT_SENSITIVITY_V_PER_A;
}

void setup() {
  Serial.begin(115200);
  delay(300);
  analogReadResolution(12);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  if (!mpu.begin()) {
    Serial.println("#ERROR,MPU6050_NOT_FOUND");
    while (true) delay(1000);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.println("time_ms,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,current_a,adc_raw");
  Serial.println("#READY,send s to start and x to stop");
}

void loop() {
  while (Serial.available() > 0) {
    const char c = static_cast<char>(Serial.read());
    if (c == 's' || c == 'S') {
      capturing = true;
      startMs = millis();
      lastSampleMs = startMs;
      Serial.println("#CAPTURE,START");
    } else if (c == 'x' || c == 'X') {
      capturing = false;
      Serial.println("#CAPTURE,STOP");
    }
  }
  if (!capturing) return;

  const uint32_t now = millis();
  if (now - lastSampleMs < SAMPLE_PERIOD_MS) return;
  lastSampleMs = now;

  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);
  const float ax_g = accel.acceleration.x / 9.80665f;
  const float ay_g = accel.acceleration.y / 9.80665f;
  const float az_g = accel.acceleration.z / 9.80665f;
  const float gx_dps = gyro.gyro.x * 57.2957795f;
  const float gy_dps = gyro.gyro.y * 57.2957795f;
  const float gz_dps = gyro.gyro.z * 57.2957795f;
  int raw = 0;
  const float currentA = readCurrentA(raw);

  Serial.printf("%lu,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%d\n",
                static_cast<unsigned long>(now - startMs),
                ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps, currentA, raw);
}
