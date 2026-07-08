# HomeGuard Security System — Lab Proof

## Pseudocode
```
CHECK safety conditions (general):
    IF temperature < 35F:
        send alert("SAFETY: Frozen pipe risk - temperature is too low!")
    IF temperature > 95F:
        send alert("SAFETY: Equipment failure risk - temperature is too high!")
    IF smoke_detected:
        send alert("SAFETY: Fire risk - smoke detected!")

IF SYSTEM_MODE == "HOME":
    IF temperature NOT IN range(65, 75):
        send notification("COMFORT: Temperature outside comfort range")
    IF door_open_duration > 5 minutes:
        send notification("COMFORT: Door left open too long")

ELSE IF SYSTEM_MODE == "AWAY":
    triggered_count = 0
    IF motion_detected:
        send alert("SECURITY: Motion Detected while in AWAY mode!")
        triggered_count += 1
    IF door_opened:
        send alert("SECURITY: DOOR OPENED while in AWAY mode!")
        triggered_count += 1
    IF triggered_count >= 2:
        send alert("SECURITY: Multiple sensors triggered - possible break-in!")

ELSE IF SYSTEM_MODE == "SLEEP":
    IF motion_detected outside bedroom:
        send alert("SECURITY: Motion detected while in SLEEP mode!")
```

## How the code works
Each sensor is represented by a Sensor object with three methods: read(), which generates a new value, isAbnormal(), which checks whether the value exceeds its threshold, and reset(), which clears the sensor state. The format_alert() function iterates through all sensors in each cycle. It first checks safety conditions regardless of the current mode, then applies the rules for HOME, AWAY, or SLEEP mode, and finally detects a possible break-in if two or more sensors are triggered while the system is in AWAY mode.
