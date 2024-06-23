#!/bin/bash
IMAGE_NAME="phi3_sample_app_image"
CONTAINER_NAME="phi3_sample_app_container"
NETWORK_NAME="phi3network"

sudo yum install -y docker
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

docker network create "$NETWORK_NAME"
docker build ./app -t "$IMAGE_NAME"
docker run -d --network=$NETWORK_NAME -p 80:8000 --name "$CONTAINER_NAME" "$IMAGE_NAME"
# docker network connect "$NETWORK_NAME" "$CONTAINER_NAME"

docker pull ollama/ollama
docker run -d --network=phi3network -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull phi3
