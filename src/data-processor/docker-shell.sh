#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export BASE_DIR=$(pwd)
export PERSISTENT_DIR=$(pwd)/../persistent-folder/
export SECRETS_DIR=$(pwd)/../secrets/
export GCP_PROJECT="brilliant-lens-421801" # CHANGE TO YOUR PROJECT ID
export GCS_BUCKET_NAME="food-planner-ml-workflow" # CHANGE TO YOUR PROJECT BUCKET
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/llm-service-account-cassie.json"
export GCP_SERVICE_ACCOUNT="llm-service-account@brilliant-lens-421801.iam.gserviceaccount.com" # CHANGE TO YOUR PROJECT ID
export LOCATION="us"
export IMAGE_NAME="food-planner-data-processor"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
$IMAGE_NAME