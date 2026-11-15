"""Check the Python <-> FlightGear connection and print live flight data.

Start FlightGear with --httpd=8080 (see README), click Fly!, then run:
    python python/check_connection.py
Press Ctrl+C to stop.
"""
import json
import time
import urllib.request

FG_URL = "http://127.0.0.1:8080"

# property path -> label shown in the output
PROPS = {
    "/position/altitude-ft": "alt ft",
    "/velocities/airspeed-kt": "IAS kt",
    "/orientation/heading-deg": "hdg",
    "/engines/engine/rpm": "rpm",
    "/controls/gear/brake-parking": "pbrake",
}


def get_prop(path):
    """Read one property from FlightGear's property tree via the HTTP JSON interface."""
    with urllib.request.urlopen(FG_URL + "/json" + path, timeout=2) as resp:
        return json.load(resp).get("value")


def main():
    try:
        version = get_prop("/sim/version/flightgear")
    except OSError as e:
        print(f"Cannot reach FlightGear at {FG_URL}: {e}")
        print("Is the sim running (past the launcher) with --httpd=8080?")
        return
    print(f"Connected to FlightGear {version}. Ctrl+C to stop.\n")

    try:
        while True:
            parts = []
            for path, label in PROPS.items():
                value = get_prop(path)
                if isinstance(value, float):
                    value = round(value, 1)
                parts.append(f"{label}: {value}")
            print(" | ".join(parts))
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
