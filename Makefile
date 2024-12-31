# Variables
TAG = 0.1
CONTAINER_NAME = pimon
PORT = 5000

# Targets
.PHONY: all build run clean

# Default target
all: build

build:
	@echo "Building Docker image with tag: $(TAG)..."
	docker build -t $(CONTAINER_NAME):$(TAG) .
	
run:
	# If there's an existing container, stop and remove it
	@echo "Stopping and removing existing container..."
	docker stop ${CONTAINER_NAME}
	docker rm ${CONTAINER_NAME}
	docker run -d --name ${CONTAINER_NAME} -p ${PORT}:${PORT} -v /media/ben/Didgeridoo:/Didgeridoo -e HOSTNAME=$(shell hostname) --privileged ${CONTAINER_NAME}:${TAG}
