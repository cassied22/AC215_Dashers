#!/bin/bash

echo "Container is running!!!"


gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
mkdir -p /mnt/gcs_bucket
gcsfuse --key-file=$GOOGLE_APPLICATION_CREDENTIALS $GCS_BUCKET_NAME /mnt/gcs_data
echo 'GCS bucket mounted at /mnt/gcs_data'
mkdir -p /app/llm_training_data
cp $CSV_SOURCE_PATH $CSV_DEST_PATH
echo "Copied $CSV_SOURCE_PATH to $CSV_DEST_PATH"
pipenv shell
