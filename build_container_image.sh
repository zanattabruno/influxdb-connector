#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if docker is installed
if ! command_exists docker; then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Define the Docker image name and tag
IMAGE_NAME="influxdb-connector"
TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

# Define the Docker Hub username and image repo
DOCKER_HUB_USERNAME="zanattabruno"
DOCKER_HUB_REPO="${DOCKER_HUB_USERNAME}/${FULL_IMAGE_NAME}"

# Build the Docker image
docker build -t "${FULL_IMAGE_NAME}" . || {
    echo "Error building Docker image."
    exit 1
}

# Tag the Docker image
docker tag "${FULL_IMAGE_NAME}" "${DOCKER_HUB_REPO}" || {
    echo "Error tagging Docker image."
    exit 1
}

# Check if user is logged in to Docker Hub
if ! docker info 2>&1 | grep -q "Username: ${DOCKER_HUB_USERNAME}"; then
    echo "Not logged in to Docker Hub or not logged in as ${DOCKER_HUB_USERNAME}. Please login and try again."
    exit 1
fi

# Push the Docker image to Docker Hub
docker push "${DOCKER_HUB_REPO}" || {
    echo "Error pushing Docker image to Docker Hub."
    exit 1
}

echo "Docker image has been pushed to Docker Hub: ${DOCKER_HUB_REPO}"
