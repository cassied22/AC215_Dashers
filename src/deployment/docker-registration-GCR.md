# GCP authentification and configuration
```sh
gcloud auth login
gcloud artifacts repositories create gcr.io \
    --repository-format=docker \
    --location=us \
    --description="Docker repository for dasher daily meal app"
gcloud services enable artifactregistry.googleapis.com
```

# Build and push docker image to GCR
```sh
gcloud auth configure-docker us-central1-docker.pkg.dev
TIMESTAMP=$(date +%Y%m%d%H%M%S)
```
Go inside `src/frontend_react` folder
```sh
docker build -t gcr.io/brilliant-lens-421801/frontend:${TIMESTAMP} --platform=linux/amd64 -f Dockerfile .
docker push gcr.io/brilliant-lens-421801/frontend:${TIMESTAMP}
```
Go inside `src/api-service` folder
```sh
docker build -t gcr.io/brilliant-lens-421801/api-service --platform=linux/amd64 -f Dockerfile .
docker push gcr.io/brilliant-lens-421801/api-service
```
Go inside `src/datapipeline` folder
```sh
docker build -t gcr.io/brilliant-lens-421801/vector-db --platform=linux/amd64 -f Dockerfile .
docker push gcr.io/brilliant-lens-421801/vector-db
```

# Useful shell scipts and commands
```sh
# View GCR Containers
gcloud container images list --repository=gcr.io/brilliant-lens-421801
gcloud container images list-tags gcr.io/brilliant-lens-421801/daily-meal-frontend-react
gcloud container images garbage-collect --repository=gcr.io/brilliant-lens-421801

# ansible playbook for registering docker images on GCR
ansible-playbook register-docker-images.yml -i inventory.yml

# Activate service account
gcloud auth activate-service-account [ACCOUNT] --key-file=KEY_FILE 
gcloud auth activate-service-account --key-file="gcp-service-cassie.json"

# Add IAM policy binding
gcloud projects add-iam-policy-binding angular-harmony-434717-n1 \
    --member="serviceAccount:gcp-service@angular-harmony-434717-n1.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.reader"

# View VM instances
gcloud compute instances list
gcloud compute ssh --project=brilliant-lens-421801 --zone=us-central1-a daily-meal-instance
```