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
            if self.value == "OPEN":
                self.opened_at = self.opened_at or datetime.now()
            else:
                self.opened_at = None

        elif self.type == "temperature":
            self.value = round(random.uniform(30, 100), 1)

        elif self.type == "smoke":
            self.value = random.choice([True, False])

    def isAbnormal(self):
        if self.type == "temperature":
            return self.value < 35 or self.value > 95
        elif self.type == "door":
            return self.value == "OPEN"
        else:
            return self.value

    def reset(self):
        self.value = None
        self.opened_at = None


def send_message(level, message):
    print(f"[{level}] {message}")
    print(f"[LOG] [{datetime.now().strftime('%H:%M:%S')}] Sending notification to homeowner...")


def format_alert(sensors, mode):
    triggered_count = 0

    for sensor in sensors:
        triggered = False

        # Safety alerts (always checked)
        if sensor.type == "temperature" and sensor.isAbnormal():

            if sensor.value < 35:
                send_message(
                    "ALERT!",
                    f"🚨HIGH: SAFETY: {sensor.name} temperature too low ({sensor.value}°F)"
                )
            else:
                send_message(
                    "ALERT!",
                    f"🚨HIGH: SAFETY: {sensor.name} temperature too high ({sensor.value}°F)"
                )

            triggered = True

        elif sensor.type == "smoke" and sensor.isAbnormal():
            send_message(
                "ALERT!",
                f"🚨HIGH: SAFETY: Smoke detected in {sensor.name}"
            )
            triggered = True

        # HOME mode
        elif mode == "HOME":

            if sensor.type == "temperature" and not (65 <= sensor.value <= 75):
                send_message(
                    "NOTIFY",
                    f"⚠️ COMFORT: {sensor.name} is outside the comfort range ({sensor.value}°F)"
                )

            elif sensor.type == "door" and sensor.opened_at:
                minutes = (datetime.now() - sensor.opened_at).total_seconds() / 60

                if minutes > 5:
                    send_message(
                        "NOTIFY",
                        f"⚠️ COMFORT: {sensor.name} has been open for {minutes:.1f} minutes"
                    )

        # AWAY mode
        elif mode == "AWAY":

            if sensor.type == "motion" and sensor.value:
                send_message(
                    "ALERT!",
                    f"🚨HIGH: SECURITY: Motion detected in {sensor.name}"
                )
                triggered = True

            elif sensor.type == "door" and sensor.value == "OPEN":
                send_message(
                    "ALERT!",
                    f"🚨 HIGH: SECURITY: {sensor.name} opened while in AWAY mode"
                )
                triggered = True

        # SLEEP mode
        elif (
            mode == "SLEEP"
            and sensor.type == "motion"
            and sensor.value
            and sensor.location != "Bedroom"
        ):
            send_message(
                "ALERT!",
                f"🚨HIGH: SECURITY: Motion detected in {sensor.name} while in SLEEP mode"
            )
            triggered = True

        if triggered:
            triggered_count += 1

    # Multiple sensor trigger
    if mode == "AWAY" and triggered_count >= 2:
        send_message(
            "ALERT!",
            "🚨HIGH: SECURITY: Multiple sensors triggered - possible break-in!"
        )

    return triggered_count


def initialize_sensors():
    return [
        Sensor("Living Room Motion", "motion", "Living Room"),
        Sensor("Front Door", "door", "Front Door"),
        Sensor("Kitchen Temperature", "temperature", "Kitchen"),
        Sensor("Bedroom Smoke", "smoke", "Bedroom"),
    ]


def run_cycle(sensors, mode, first=False, forced=None):
    forced = forced or {}

    if first:
        print("=== HomeGuard Security System ===")
        print(f"Mode: {mode}")

    print(f"\nTime: {datetime.now().strftime('%H:%M:%S')}")

    for sensor in sensors:

        if sensor.name in forced:
            sensor.value = forced[sensor.name]

            if sensor.type == "door" and sensor.value == "OPEN":
                sensor.opened_at = sensor.opened_at or datetime.now()

        else:
            sensor.read()

        print(f"[READING] {sensor.name}: {sensor.value}")

    format_alert(sensors, mode)


if __name__ == "__main__":

    print("---------- TEST 1: SECURITY (AWAY) ----------")
    sensors = initialize_sensors()

    run_cycle(sensors, "AWAY", first=True)

    run_cycle(
        sensors,
        "AWAY",
        forced={
            "Front Door": "OPEN",
            "Living Room Motion": True,
        },
    )

    print("\n---------- TEST 2: SAFETY ----------")
    sensors = initialize_sensors()

    run_cycle(
        sensors,
        "HOME",
        first=True,
        forced={
            "Kitchen Temperature": 20,
            "Bedroom Smoke": True,
        },
    )

    print("\n---------- TEST 3: COMFORT (HOME) ----------")
    sensors = initialize_sensors()

    run_cycle(
        sensors,
        "HOME",
        first=True,
        forced={
            "Kitchen Temperature": 97,
        },
    )

    sensors[1].value = "OPEN"
    sensors[1].opened_at = datetime.now() - timedelta(minutes=6)

    run_cycle(
        sensors,
        "HOME",
        forced={
            "Front Door": "OPEN",
        },
    )

    print("\n---------- TEST 4: SLEEP MODE ----------")
    sensors = initialize_sensors()

    run_cycle(
        sensors,
        "SLEEP",
        first=True,
        forced={
            "Living Room Motion": True,
        },
    )