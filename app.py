import os
import psutil
from flask import Flask, render_template_string, url_for

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
    cpu_avg, cpu_per_core = get_cpu_usage()

    # Generate CPU usage rows
    cpu_usage_rows = f"<tr><td>Average CPU Usage</td><td>{cpu_avg:.2f}%</td></tr>"
    for i, core in enumerate(cpu_per_core):
        cpu_usage_rows += f"<tr><td>Core {i} Usage</td><td>{core:.2f}%</td></tr>"

    # Generate HTML content
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{hostname} Status</title>
        <link rel="stylesheet" href="{url_for('static', filename='styles.css')}">
    </head>
    <body>
        <h1>{hostname} Status</h1>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Temperature</td><td>{temp}</td></tr>
            {cpu_usage_rows}
        </table>
        <footer>&copy; 2024 Raspberry Pi Monitor</footer>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

