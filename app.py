import os
from flask import Flask
import psutil

app = Flask(__name__)

def get_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_milli = int(f.read().strip())
            temp = temp_milli / 1000.0  # Convert to Celsius
            return f"{temp:.2f}°C"
    except Exception as e:
        return f"Error: {e}"

def get_cpu_usage():
    try:
        # CPU usage per core
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        # Average CPU usage
        cpu_avg = psutil.cpu_percent(interval=1)
        return cpu_avg, cpu_per_core
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def status():
    temp = get_temperature()
    hostname = os.environ.get("HOSTNAME", "unknown")
    
    # Get CPU usage details
    cpu_avg, cpu_per_core = get_cpu_usage()
    cpu_usage_table = "<tr><td>Average CPU Usage</td><td>{:.2f}%</td></tr>".format(cpu_avg)
    for i, core in enumerate(cpu_per_core):
        cpu_usage_table += f"<tr><td>Core {i} Usage</td><td>{core:.2f}%</td></tr>"
    
    temperature_table = f"<tr><td>Temperature</td><td>{temp}</td></tr>"
    
    # Combine everything into a single HTML table
    html_table = f"""
    <table border="1">
        {temperature_table}
        {cpu_usage_table}
    </table>
    """
    return f"<h1>{hostname} Status</h1>{html_table}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

