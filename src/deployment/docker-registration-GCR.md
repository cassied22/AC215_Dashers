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

```sh
# View GCR Containers
gcloud container images list --repository=gcr.io/brilliant-lens-421801
gcloud container images list-tags gcr.io/brilliant-lens-421801/daily-meal-frontend-react
gcloud container images garbage-collect --repository=gcr.io/brilliant-lens-421801
```

```sh
ansible-playbook register-docker-images.yml -i inventory.yml
```