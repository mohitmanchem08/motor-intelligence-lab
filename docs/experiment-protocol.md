# Bench Experiment Protocol

## Before each run
- Record motor, driver, supply, sensor module, ESP32 board and firmware commit.
- Check grounds and verify ADC voltage range.
- Secure the motor and guard moving parts.
- Confirm the driver is rated for stall current; do not deliberately stall the motor.
- Calibrate current zero with motor off and compare current against a suitable meter/reference load.

## Procedure
1. Start with a no-load motor test at low, safe duty cycle.
2. Record at least three runs under identical conditions.
3. Remove power before changing wiring or mechanical load.
4. Use a repeatable guarded fixture for load comparisons; never impede a shaft with fingers or loose material.
5. Keep raw CSV captures immutable and document each setup.

## Report
Report sample count, duration, sampling interval distribution, current statistics and acceleration magnitude RMS. Include uncertainty and note clipped ADC readings or dropped samples. Do not label a condition a fault without independent ground truth.
