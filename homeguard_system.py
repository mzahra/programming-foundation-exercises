import random
from datetime import datetime, timedelta

class Sensor:
    def __init__(self, name, sensor_type, location):
        self.name = name
        self.type = sensor_type
        self.location = location
        self.value = None
        self.opened_at = None

    def read(self):
        if self.type == "motion":
            self.value = random.choice([True, False])
        elif self.type == "door":
            self.value = random.choice(["OPEN", "CLOSED"])
            if self.value == "OPEN" and self.opened_at is None:
                self.opened_at = datetime.now()
            elif self.value == "CLOSED":
                self.opened_at = None
        elif self.type == "temperature":
            self.value = round(random.uniform(30, 100), 1)
        elif self.type == "smoke":
            self.value = random.choice([True, False])
        return self.value

    def isAbnormal(self):
        if self.type == "temperature":
            return self.value < 35 or self.value > 95
        if self.type in ("motion", "smoke"):
            return self.value is True
        if self.type == "door":
            return self.value == "OPEN"
        return False

    def reset(self):
        self.value = None
        self.opened_at = None


def format_alert(sensors, mode):
    triggered_count = 0

    for sensor in sensors:
        triggered = False

        # safety checks: always run, regardless of mode
        if sensor.type == "temperature" and sensor.isAbnormal():
            if sensor.value < 35:
                msg = f"SAFETY: {sensor.name} temp {sensor.value}F - frozen pipe risk!"
            elif sensor.value > 95:
                msg = f"SAFETY: {sensor.name} temp {sensor.value}F - equipment failure risk!"
            print(f"[ALERT!] 🚨 HIGH: {msg}")
            print(f"[LOG] [{datetime.now().strftime('%H:%M:%S')}] Sending notification to homeowner...")
            triggered = True

        elif sensor.type == "smoke" and sensor.isAbnormal():
            print(f"[ALERT!] 🚨 HIGH: SAFETY: Smoke detected in {sensor.name}!")
            print(f"[LOG] [{datetime.now().strftime('%H:%M:%S')}] Sending notification to homeowner...")
            triggered = True

        # mode-based checks
        elif mode == "HOME":
            if sensor.type == "temperature" and not (65 <= sensor.value <= 75):
                print(f"[NOTIFY] ⚠️ COMFORT: {sensor.name} outside comfort range ({sensor.value}°F)")
                triggered = True
            elif sensor.type == "door" and sensor.opened_at:
                minutes_open = (datetime.now() - sensor.opened_at).total_seconds() / 60
                if minutes_open > 5:
                    print(f"[NOTIFY] ⚠️ COMFORT: {sensor.name} left open too long ({minutes_open:.1f} min)")
                    triggered = True

        elif mode == "AWAY":
            if sensor.type == "motion" and sensor.value:
                print(f"[ALERT!] 🚨 HIGH: SECURITY: Motion detected in {sensor.name} while in AWAY mode!")
                print(f"[LOG] [{datetime.now().strftime('%H:%M:%S')}] Sending notification to homeowner...")
                triggered = True
            elif sensor.type == "door" and sensor.value == "OPEN":
                print(f"[ALERT!] 🚨 HIGH: SECURITY: {sensor.name} opened while in AWAY mode!")
                print(f"[LOG] [{datetime.now().strftime('%H:%M:%S')}] Sending notification to homeowner...")
                triggered = True

        elif mode == "SLEEP" and sensor.type == "motion" and sensor.value and sensor.location != "Bedroom":
            print(f"[ALERT!] 🚨 HIGH: SECURITY: Motion detected in {sensor.name} while in SLEEP mode!")
            print(f"[LOG] [{datetime.now().strftime('%H:%M:%S')}] Sending notification to homeowner...")
            triggered = True

        if triggered:
            triggered_count += 1

    # multi-sensor break-in check
    if mode == "AWAY" and triggered_count >= 2:
        print("[ALERT!] 🚨 HIGH: SECURITY: Multiple sensors triggered - possible break-in!")
        print(f"[LOG] [{datetime.now().strftime('%H:%M:%S')}] Sending notification to homeowner...")

    return triggered_count

def initialize_sensors():
    return [
        Sensor("Living Room Motion", "motion", "Living Room"),
        Sensor("Front Door", "door", "Front Door"),
        Sensor("Kitchen Temperature", "temperature", "Kitchen"),
        Sensor("Bedroom Smoke", "smoke", "Bedroom"),
    ]
 
 
def run_cycle(sensors, mode, is_first=False, forced_values=None):
    """Runs one reading cycle: prints header/time, reads sensors, checks alerts."""
    forced_values = forced_values or {}
 
    if is_first:
        print("=== HomeGuard Security System ===")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Mode: {mode}\n")
    else:
        print(f"\nTime: {datetime.now().strftime('%H:%M:%S')}")
 
    for s in sensors:
        if s.name in forced_values:
            s.value = forced_values[s.name]
            if s.type == "door" and s.value == "OPEN" and s.opened_at is None:
                s.opened_at = datetime.now()
        else:
            s.read()
        print(f"[READING] {s.name}: {s.value}")
 
    format_alert(sensors, mode)
 
 
if __name__ == "__main__":
    print("----------TEST 1: SECURITY (AWAY)--------")
    sensors = initialize_sensors()
    run_cycle(sensors, "AWAY", is_first=True)
    run_cycle(sensors, "AWAY", forced_values={"Front Door": "OPEN", "Living Room Motion": True})
 
    print("\n----------TEST 2: SAFETY------")
    sensors = initialize_sensors()
    run_cycle(sensors, "HOME", is_first=True,
              forced_values={"Kitchen Temperature": 20, "Bedroom Smoke": True})
 
    print("\n----------TEST 3: COMFORT (HOME)-------")
    sensors = initialize_sensors()
    run_cycle(sensors, "HOME", is_first=True, forced_values={"Kitchen Temperature": 97})
    door = sensors[1]
    door.value = "OPEN"
    door.opened_at = datetime.now() - timedelta(minutes=6)
    run_cycle(sensors, "HOME", forced_values={"Front Door": "OPEN"})
 
    print("\n----------TEST 4: SLEEP MODE-------")
    sensors = initialize_sensors()
    run_cycle(sensors, "SLEEP", is_first=True, forced_values={"Living Room Motion": True})