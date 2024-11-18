#!/bin/bash

set -e
export IMAGE_NAME="food-detection"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run -v $(pwd)/../../tests/$IMAGE_NAME:/app/tests -it $IMAGE_NAME
# docker-compose up