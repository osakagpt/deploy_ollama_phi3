#!/bin/bash
IMAGE_NAME="phi3_sample_app_image"
CONTAINER_NAME="phi3_sample_app_container"

sudo usermod -a -G docker ec2-user

docker stop "$CONTAINER_NAME"
docker rm "$CONTAINER_NAME"
docker rmi "$IMAGE_NAME"
docker stop "ollama"
docker rm "ollama"
