import os
from flask import Flask

app = Flask(__name__)

def get_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_milli = int(f.read().strip())
            temp = temp_milli / 1000.0  # Convert to Celsius
            return f"{temp:.2f}°C"
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def temperature():
    temp = get_temperature()
    hostname = os.environ.get("HOSTNAME", "unknown")
    temperature_table = f"<table><tr><td>Temperature</td><td>{temp}</td></tr></table>"
    return f"<h1>{hostname} status</h1>{temperature_table}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

