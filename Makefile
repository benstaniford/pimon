# Variables
TAG = latest
DOCKER_USERNAME = nerwander
CONTAINER_NAME = pimon
PORT = 5000

# Targets
.PHONY: all build run clean

# Default target
all: build

build:
	@echo "Building Docker image with tag: $(TAG)..."
	docker build -t $(CONTAINER_NAME):$(TAG) .

clean:
	@echo "Removing Docker image with tag: $(TAG)..."
	docker stop ${CONTAINER_NAME}
	docker rm ${CONTAINER_NAME}
	docker rmi $(CONTAINER_NAME):$(TAG)
	
run:
	docker run -d --name ${CONTAINER_NAME} -p ${PORT}:${PORT} -e HOSTNAME=$(shell hostname) --privileged ${CONTAINER_NAME}:${TAG}

push:
	@echo "Pushing Docker image with tag: $(TAG)..."
	docker tag $(CONTAINER_NAME):$(TAG) $(DOCKER_USERNAME)/$(CONTAINER_NAME):$(TAG)
	docker push $(DOCKER_USERNAME)/$(CONTAINER_NAME):$(TAG)
