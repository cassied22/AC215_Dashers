# ML Pipeline Workflow

This folder contains an ML pipeline workflow that automates the data processing, model training, and evaluation for our food planner application. 

## Key Components

* `build_docker.yml`: An Ansible playbook that handles building and pushing Docker images to Google Container Registry (GCR). It builds separate images for data processing, model training, and model evaluation components. This can be manually triggered using: ```ansible-playbook build_docker.yml -e "gcp_project=$GCP_PROJECT"```

* Individual Pipeline Components:
   - `data-processor-pipeline.yaml`: Handles data preprocessing, including cleaning, preparation, and uploading to GCS bucket
   - `model-training-pipeline.yaml`: Manages model training using the processed data from GCS
   - `model-evaluation-pipeline.yaml`: Executes model evaluation and validates performance metrics

These are triggered by either:
1. Manual local run:
   python cli.py --pipeline

2. Through GitHub Actions:
   When ml_pipeline.yaml workflow runs and calls pipeline.yaml
   
* `pipeline.yaml`: The main configuration file that orchestrates how the individual pipeline components work together in Vertex AI.


### GitHub Actions Integration:
   - `.github/workflows/ml_pipeline.yaml`: Automates the CI/CD process by:
     1. Building and pushing Docker images to GCR
     2. Deploying the pipeline to Vertex AI
     3. Triggering when changes are pushed to the `hanna_mlworkflow` branch
## Workflow Process

1. Development starts locally using `docker-shell.sh` for testing
2. When code is pushed to GitHub, the workflow automatically:
  - Builds fresh Docker images
  - Pushes them to GCR
  - Deploys the pipeline to Vertex AI
3. The pipeline executes in sequence: data processing → model training → evaluation