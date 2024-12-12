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

# Kubernetes setup
```sh
ansible-playbook deploy-k8s-create-cluster.yml -i inventory.yml --extra-vars cluster_state=present
ansible-playbook deploy-k8s-setup-containers.yml -i inventory.yml --extra-vars cluster_state=present
```

# Kubernetes inspection commands
```sh
# Check cluster status and namespaces
kubectl get all
kubectl get all --all-namespaces
kubectl get pods --all-namespaces
kubectl get pods -n daily-meal-cluster-namespace
kubectl get componentstatuses
kubectl get nodes
kubectl describe pod api-7687bf556d-pbw64 -n daily-meal-cluster-namespace


wget -qO- http://api:9000/llm-food-detection/chats


# Check the init container logs:
kubectl logs -n daily-mean-cluster-namespace job/vector-db-loader -c wait-for-chromadb

# Check the main container logs:
kubectl logs -n daily-meal-cluster-namespace job/vector-db-loader -c vector-db-loader
kubectl logs -n daily-meal-cluster-namespace pod/api-7687bf556d-pbw64 
kubectl logs api-7687bf556d-pbw64 -n daily-meal-cluster-namespace

# Check the job status:
kubectl describe job vector-db-loader -n daily-meal-cluster-namespace



# First, find the pod name for your job
kubectl get pods -n daily-meal-cluster-namespace | grep vector-db-loader

# Then get the logs from that pod (replace <pod-name> with the actual name)
kubectl logs -n cheese-app-cluster-namespace <pod-name>
kubectl logs -n daily-meal-cluster-namespace vector-db-loader-5t8vw 

# If you want to see logs from the init container specifically
kubectl logs -n cheese-app-cluster-namespace <pod-name> -c wait-for-chromadb
kubectl logs -n cheese-app-cluster-namespace vector-db-loader-wlfdx -c wait-for-chromadb

# If you want to see logs from the main container
kubectl logs -n cheese-app-cluster-namespace <pod-name> -c vector-db-loader
kubectl logs -n cheese-app-cluster-namespace vector-db-loader-wlfdx -c vector-db-loader

# You can also get logs directly from the job (this will show logs from the most recent pod)
kubectl logs job/vector-db-loader -n cheese-app-cluster-namespace

# To see previous logs if the pod has restarted
kubectl logs job/vector-db-loader -n cheese-app-cluster-namespace --previous


# View logs from the current API pod
kubectl logs deployment/api -n cheese-app-cluster-namespace

# Follow the logs
kubectl logs deployment/api -n cheese-app-cluster-namespace -f
```

# Useful shell scipts and commands
```sh
# View GCR Containers
gcloud container images list --repository=gcr.io/brilliant-lens-421801
gcloud container images list-tags gcr.io/brilliant-lens-421801/daily-meal-vector-db-cli
gcloud container images garbage-collect --repository=gcr.io/brilliant-lens-421801

# ansible playbook for registering docker images on GCR
ansible-playbook deploy-register-docker-images.yml -i inventory.yml
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present
ansible-playbook deploy-provision-instance.yml -i inventory.yml
ansible-playbook deploy-setup-containers.yml -i inventory.yml
ansible-playbook deploy-setup-webserver.yml -i inventory.yml
# delete the compute instance
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=absent

# Check status of GCP VM containers
sudo docker container ls
sudo docker container logs api-service -f
sudo docker container logs frontend -f
sudo docker container logs nginx -f
# Go into GCP VM container shells
sudo docker exec -it api-service /bin/bash
sudo docker exec -it frontend /bin/bash
sudo docker exec -it nginx /bin/bash

# Activate service account
gcloud auth activate-service-account [ACCOUNT] --key-file=KEY_FILE 
gcloud auth activate-service-account --key-file="gcp-service-cassie.json"

# Add IAM policy binding
gcloud projects add-iam-policy-binding brilliant-lens-421801 \
    --member="serviceAccount:llm-service-account@brilliant-lens-421801.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

# View VM instances
gcloud compute instances list
gcloud compute ssh --project=brilliant-lens-421801 --zone=us-central1-a daily-meal-instance
```