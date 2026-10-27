# Wiring and Electrical Safety

| Signal | Example classic ESP32 pin | Notes |
|---|---|---|
| MPU6050 SDA | GPIO 21 | Verify 3.3 V compatibility |
| MPU6050 SCL | GPIO 22 | Verify 3.3 V compatibility |
| ACS712 analog output | GPIO 34 through a validated interface | Board-specific ADC pin |
| Ground | GND | Common signal reference where required |

Power modules only within their documented voltage range. Some MPU6050 breakouts include regulation/level shifting; others do not.

## ACS712 interface
Many ACS712 modules use 5 V and output around half their supply voltage at zero current. That output may exceed ESP32 ADC limits. Before connecting, read the exact module documentation, measure zero-current output, calculate a divider/buffer for the full output range, and verify voltage at the ESP32 pin with a multimeter. Recalculate `CURRENT_ZERO_V`, `CURRENT_SENSITIVITY_V_PER_A`, and `ADC_DIVIDER_RATIO` for your circuit. A compatible 3.3 V current sensor may be simpler.

## Motor circuit
Never drive a DC motor directly from an ESP32 GPIO. Use a motor driver rated for motor stall current, supply voltage and thermal load. Keep motor power disconnected while checking wiring. Do not improvise an H-bridge from small-signal transistors without engineering the drive, losses, flyback paths and thermal limits.

## Physical setup photos

No physical setup photograph is included because the hardware configuration has not been photographed and verified for this repository. Add your own real photo here after assembly, with the exact sensor module and voltage interface visible. Do not use a generated image as hardware proof.
