#!/bin/bash

echo "Container is running!!!"

args="$@"
echo $args

# Authenticate with gcloud
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

if [[ -z ${args} ]]; 
then
    pipenv shell
else
  pipenv run python $args
fi