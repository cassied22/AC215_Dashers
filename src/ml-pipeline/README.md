# Machine Learning Workflow

This module focus on the Machine Learning workflow, which contains the following main conponents: Data Processor, Model Training/Deployment, Model Evaluation. 

# Setup Instructions

- Run docker container in this folder by using:
```chmod +x docker-shell.sh```
```sh docker-shell.sh```

- Run Data Processor in the Docker Container by using:
```python cli.py --data_processor```

- Run Model Training in the Docker Container by using:
```python cli.py --model_training```

- Run Model Evaluation in the Docker Container by using:
```python cli.py --model_evaluation```

- Run Entire Machine Learning Pipelin (including data process, model training/devlopment, and eveluation) by using:
```python cli.py --pipeline```

<hr style="height:2px;border-width:0;color:gray;background-color:gray">
Please noted that during our model training step, since we are finetuning the gemini model in Vertex AI using SupervisedTuningJob, it will get automatically deployed to an endpoint on vertex ai upon the completion of the training job, we did not have a separate function for model deployment.
<hr style="height:2px;border-width:0;color:gray;background-color:gray">


# Automated Data Processing, Model Training and Machine Learning Pipeline  in github action
We have set up the CI/CD pipeline to automate the machine learning workflow in github action. Workflow file[../../.github/workflows/ml-pipeline.yml])

To run Machine Learning Pipelines on updates to the codebase, add the following to code commit comment:
* Add `/run-ml-pipeline` to the commit message to run the entire ML pipeline
* Add `/run-model-training` to the commit message to run the model training/deployment
* Add `/run-data-processor` to the commit message to run the data processor 

# Screenshot of Succesful Data/Processing, Model Training, Machine Learning Pipeline workflow runs
### Machine Learning Pipeline
![](../../images/ml_workflow/ml_pipeline1.png)
![](../../images/ml_workflow/ml_pipeline2.png)

### Model Training
![](../../images/ml_workflow/ml_training2.png)
![](../../images/ml_workflow/ml_training1.png)

### Data Processor
![](../../images/ml_workflow/ml_process1.png)
![](../../images/ml_workflow/ml_process2.png)

# Documentation on details of ML Pipeline

## Data Processor:
For data processing, we first download the raw recipe data (original source: https://recipenlg.cs.put.poznan.pl/), which has been previously uploaded to GCP bucket. Then we perform data cleaning by removing duplicates and nulls. 
* Model Training and Deployment: Submits training jobs to Vertex AI to train models
* Model Deploy: Updates trained models signature with preprocessing logic added to it. Upload model to Vertex AI Model Registry and Deploy model to Model Endpoints.
* API Service: FastAPI service to expose APIs to the frontend.
* Frontend:  React Frontend for the cheese app.
<img src="images/ci-cd.png"  width="800">


<hr style="height:2px;border-width:0;color:gray;background-color:gray">

NOTE: You can skip the following steps if you have already completed the previous tutorial and have a running Kubernetes cluster. 
Instead you can start from the [View the App](#view-the-app-if-you-have-a-domain) section below.

<hr style="height:2px;border-width:0;color:gray;background-color:gray">


 `deployment.json`

