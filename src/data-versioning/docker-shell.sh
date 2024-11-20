#!/bin/bash

set -e

export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../secrets/
export GCS_BUCKET_NAME="ac215vm-dvc-store"
export GCP_PROJECT="ac215vm"
export GCP_ZONE="us-central1-a"
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/demo-service-account.json"
export CSV_SOURCE_PATH="/mnt/gcs_data/data/recipe_qa.csv"
export CSV_DEST_PATH="/app/llm_training_data/recipe_qa.csv"

echo "Building image"
docker build -t data-version-cli -f Dockerfile .

echo "Running container"
docker run --rm --name data-version-cli -ti \
--privileged \
--cap-add SYS_ADMIN \
--device /dev/fuse \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v ~/.gitconfig:/etc/gitconfig \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e CSV_SOURCE_PATH=$CSV_SOURCE_PATH \
-e CSV_DEST_PATH=$CSV_DEST_PATH \
data-version-cli