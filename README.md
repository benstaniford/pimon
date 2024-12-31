# pimon
A very simple docker container for showing the temperature, CPU utilisation and disk status of a Raspberry Pi requiring no prerequisites

## Screenshot

![Screenshot](https://raw.githubusercontent.com/benstaniford/pimon/main/readme/screen.png)

## Flask Web App Deployment Instructions (nerwander/pimon)

### **To Install the Docker Image from Docker Hub**

To install and run the `nerwander/pimon` Flask web app from Docker Hub, follow these steps:

#### Prerequisites:
- Make sure Docker is installed on your machine. You can download Docker from the official website: [Install Docker](https://docs.docker.com/get-docker/) although for the Raspberry Pi 5, I found 
[this guide](https://www.jpaul.me/2024/07/how-to-install-docker-on-a-raspberry-pi-5/) to be the most helpful.

#### Pull the Docker Image
To pull the image from Docker Hub, open a terminal and run the following command:

```bash
docker pull nerwander/pimon:latest
```

### **Running the Container via Docker**

#### Once the image is pulled, you can run the Flask web app in a container. However, there are a few things to note:

Volumes must be added for the disk status to work. You should mount any directories you want to check the disk usage for.
Set the HOSTNAME environment variable to specify the hostname of your Raspberry Pi (or the system where the app is running).

#### Run the following command to start the container with the necessary volumes and environment variable, the disk usage will be shown for the mounted directories:

```bash
docker run -d -p 5000:5000 \
  -e HOSTNAME=<your_hostname> \
  -v /path/to/volume1:/volume1 \
  -v /path/to/volume2:/volume2 \
  nerwander/pimon:latest
```



