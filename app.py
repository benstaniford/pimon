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

        # Filter the results to find volumes (usually those with '/mnt' or '/volumes' paths)
        volumes = []
        for line in result.stdout.splitlines():
            if ' on ' in line:
                parts = line.split(' on ')
                source = parts[0].strip()
                target = parts[1].split(' ')[0].strip()  # Path where the volume is mounted
                volumes.append(target)

        volumes = [v for v in volumes if os.path.isdir(v)]
        volumes = [v for v in volumes if not v.startswith(('/dev/', '/etc/', '/proc/', '/sys/'))]
        volumes = [v for v in volumes if not v == '/dev' or v == '/etc' or v == '/proc' or v == '/sys']


        return volumes

    except Exception as e:
        print(f"Error retrieving mounted volumes: {e}")
        return []

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
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        cpu_avg = psutil.cpu_percent(interval=1)
        return cpu_avg, cpu_per_core
    except Exception as e:
        return f"Error: {e}"

def generate_sizes_and_units(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    for unit in units:
        if size < 1024:
            return size, unit
        size /= 1024
    return size, units[-1]

def generate_disk_pie_chart(volume_path):
    try:
        usage = psutil.disk_usage(volume_path)
        labels = ['Used', 'Free']
        sizes = [usage.used, usage.free]
        colors = ['#d65d0e', '#458588']  # Gruvbox orange and aqua
        explode = (0.1, 0)  # Slightly offset the 'Used' slice

        # Set the labels to be gruvbox white
        plt.rcParams['text.color'] = '#ebdbb2'

        [used_size, used_units] = generate_sizes_and_units(usage.used)
        [free_size, free_units] = generate_sizes_and_units(usage.free)

        # Create the pie chart
        plt.figure(figsize=(4, 4))
        plt.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.1f%%', 
            startangle=140, 
            explode=explode, 
            shadow=True
        )
        plt.title(
            f"Disk Usage: {volume_path}\n"
            f"Used: {used_size:.2f} {used_units}, Free: {free_size:.2f} {free_units}",
            color="#ebdbb2"
        )
        plt.axis('equal')  # Equal aspect ratio ensures a circular pie chart

        # Save the chart to a file
        chart_path = f"static/{volume_path.strip('/').replace('/', '_')}_disk.png"
        plt.savefig(chart_path, transparent=True, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        return chart_path
    except Exception as e:
        return None


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
        chart_path = generate_disk_pie_chart(volume)
        if chart_path:
            disk_charts += f"""
            <div>
                <img src='/{chart_path}' alt='Disk Usage for {volume}'>
                <p>{volume}</p>
            </div>
            """

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
