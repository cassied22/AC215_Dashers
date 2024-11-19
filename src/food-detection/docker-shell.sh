#!/bin/bash

set -e
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../secrets/
export IMAGE_NAME="food-detection"
export GOOGLE_API_KEY="/secrets/gemini-key.json"
export OPENAI_API_KEY="/secrets/openai-key.json"

docker build -t $IMAGE_NAME -f Dockerfile .

docker run -v $(pwd)/../../tests/$IMAGE_NAME:/app/tests \
           -v "$BASE_DIR":/app \
           -v $SECRETS_DIR:/secrets \
           -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
           -e OPENAI_API_KEY=$OPENAI_API_KEY \
           -it $IMAGE_NAME
# docker-compose up