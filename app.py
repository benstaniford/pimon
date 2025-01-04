import os
import psutil
import subprocess
import matplotlib.pyplot as plt
from flask import Flask, render_template_string, url_for, send_file

app = Flask(__name__)

def get_mounted_volumes():
    try:
        result = subprocess.run(['mount'], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception("Failed to retrieve mount points")

        volumes = []
        for line in result.stdout.splitlines():
            if ' on ' in line:
                parts = line.split(' on ')
                source = parts[0].strip()
                target = parts[1].split(' ')[0].strip()
                volumes.append(target)

        volumes = [v for v in volumes if os.path.isdir(v)]
        volumes = [v for v in volumes if not v.startswith(('/dev/', '/etc/', '/proc/', '/sys/'))]

        return volumes

    except Exception as e:
        print(f"Error retrieving mounted volumes: {e}")
        return []

def get_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_milli = int(f.read().strip())
            temp = temp_milli / 1000.0
            return f"{temp:.2f}°C"
    except Exception as e:
        return f"Error: {e}"

def get_cpu_usage():
    try:
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        cpu_avg = psutil.cpu_percent(interval=1)
        return cpu_avg, cpu_per_core
    except Exception as e:
        return f"Error: {e}"

def generate_pie_chart(data, labels, title, filename):
    try:
        colors = ['#d65d0e', '#458588']
        explode = (0.1, 0)
        plt.rcParams['text.color'] = '#ebdbb2'

        plt.figure(figsize=(4, 4))
        plt.pie(
            data,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=140,
            explode=explode,
            shadow=True
        )
        plt.title(title, color="#ebdbb2")
        plt.axis('equal')
        chart_path = f"static/{filename}"
        plt.savefig(chart_path, transparent=True, bbox_inches='tight')
        plt.close()
        return chart_path
    except Exception as e:
        print(f"Error generating pie chart: {e}")
        return None

def generate_memory_charts():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    ram_chart = generate_pie_chart(
        [mem.used, mem.available],
        ['Used', 'Available'],
        "RAM Usage",
        "ram_usage.png"
    )

    swap_chart = generate_pie_chart(
        [swap.used, swap.free],
        ['Used', 'Free'],
        "SWAP Usage",
        "swap_usage.png"
    )

    return ram_chart, swap_chart

@app.route("/")
def status():
    temp = get_temperature()
    hostname = os.environ.get("HOSTNAME", "unknown")
    cpu_avg, cpu_per_core = get_cpu_usage()

    cpu_usage_rows = f"<tr><td>Average CPU Usage</td><td>{cpu_avg:.2f}%</td></tr>"
    for i, core in enumerate(cpu_per_core):
        cpu_usage_rows += f"<tr><td>Core {i} Usage</td><td>{core:.2f}%</td></tr>"

    volumes = get_mounted_volumes()
    disk_charts = ""
    for volume in volumes:
        chart_path = generate_pie_chart(
            [psutil.disk_usage(volume).used, psutil.disk_usage(volume).free],
            ['Used', 'Free'],
            f"Disk Usage: {volume}",
            f"{volume.strip('/').replace('/', '_')}_disk.png"
        )
        if chart_path:
            disk_charts += f"""
            <div>
                <img src='/{chart_path}' alt='Disk Usage for {volume}'>
                <p>{volume}</p>
            </div>
            """

    ram_chart, swap_chart = generate_memory_charts()

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{hostname} status</title>
        <link rel="stylesheet" href="{url_for('static', filename='styles.css')}">
        <link rel="icon" href="static/favicon.png" type="image/png">
    </head>
    <body>
        <h1>{hostname} status</h1>

        <h2>CPU Usage</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Temperature</td><td>{temp}</td></tr>
            {cpu_usage_rows}
        </table>

        <h2>Memory Usage</h2>
        <div class="pie-chart-container">
            <div>
                <img src='/{ram_chart}' alt='RAM Usage'>
                <p>RAM</p>
            </div>
            <div>
                <img src='/{swap_chart}' alt='SWAP Usage'>
                <p>SWAP</p>
            </div>
        </div>

        <h2>Disk Usage</h2>
        <div class="pie-chart-container">
            {disk_charts}
        </div>

        <footer>&copy; 2024 Ben Staniford</footer>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

