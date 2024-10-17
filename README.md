## Milestone 2

<!-- ```
The files are empty placeholders only. You may adjust this template as appropriate for your project.
Never commit large data files,trained models, personal API Keys/secrets to GitHub
``` -->

#### Project Milestone 2 Organization

```
├── Readme.md
├── data # DO NOT UPLOAD DATA TO GITHUB, only .gitkeep to keep the directory or a really small sample
├── notebooks
│   └── eda.ipynb
├── references
├── reports
│   └── Statement of Work_Sample.pdf
└── src
    ├── datapipeline
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── dataloader.py
    │   ├── docker-shell.sh
    │   ├── preprocess_cv.py
    │   ├── preprocess_rag.py
    ├── docker-compose.yml
    └── models
        ├── Dockerfile
        ├── docker-shell.sh
        ├── infer_model.py
        ├── model_rag.py
        └── train_model.py
```

# AC215 - Milestone2 - Daily Meal Assistant - "What to Eat Today"

**Team Members**
Hanqi Zeng(hanqizeng@hsph.harvard.edu)  <br/> 
Chris Wang(ywang3@hsph.harvard.edu)   <br/> 
Selina Qian(jingyun_qian@hsph.harvard.edu) <br/> 
Shiyu Ma(shiyuma@g.harvard.edu)  <br/> 
Cassie Dai(cdai@g.harvard.edu) <br/> 


**Group Name**
Dashers

**Project**
In this project, we aim to develop an app that serves as a personal meal assistant, helping users track their available ingredients, suggest healthy recipes, and recommend nearby restaurants based on user preferences and current inventory. The app will combine advanced AI tools like object detection and large language models (LLMs) to provide tailored meal recommendations and route suggestions for dining out.

### Milestone2 ###

In this milestone, we have the components for data management, including versioning, as well as the computer vision and language models.

**Data**
We gathered a dataset of 2,231,150 recipes including title (dish name), ingredients, directions, retrieved link, source type, and named entity recognition (NER) for food items. The ingredients are listed as an array of strings. The directions are provided as an array of strings, with each string representing a step in the cooking process. The NER data consists of an array of food item names extracted from the recipe. The dataset, approximately 2.29 GB in size, was collected from the following source: https://huggingface.co/datasets/mbien/recipe_nlg. We have stored it in a private Google Cloud Bucket.

**Data Pipeline Containers**
1. One container processes the 100GB dataset by resizing the images and storing them back to Google Cloud Storage (GCS).

	**Input:** Source and destination GCS locations, resizing parameters, and required secrets (provided via Docker).

	**Output:** Resized images stored in the specified GCS location.

2. Another container prepares data for the RAG model, including tasks such as chunking, embedding, and populating the vector database.

## Data Pipeline Overview

1. **`src/datapipeline/preprocess_cv.py`**

2. **`src/datapipeline/preprocess_rag.py`**
   This script handles preprocessing on our 2.29 GB dataset. It does data cleaning and feature selection to enable faster iteration during processing. The preprocessed dataset is now reduced to XX GB and stored on GCS.
   This script also prepares the necessary data for setting up our vector database. It performs chunking, embedding, and loads the data into a vector database (ChromaDB).

3. **`src/datapipeline/Pipfile`**
   We used the following packages to help with preprocessing:
   <!-- - `special cheese package` -->

4. **`src/preprocessing/Dockerfile(s)`**
   Our Dockerfiles follow standard conventions, with the exception of some specific modifications described in the Dockerfile/described below.


## Running Dockerfile
Go to a terminal inside datapipeline
- Run docker container by using:
```sh docker-shell.sh```

**Models container**
- This container has scripts for model training, rag pipeline and inference
- Instructions for running the model container

Mock Submission

To open the container:

Send an email to hanqizenghannanana@gmail.com with your email address associated with your GCP account. We would add you as an editor to our GCP project.
[Login GCP, select project id, our ```x-goog-project-id``` is ac215vm, start the VM instance]
Open a GCP terminal, change directory into /home/cassied22/AC215_Dashers/src/datapipeline folder
Run docker-shell.sh using command: ```sudo sh docker-shell.sh```
Inside the container, run preprocessing using command: ```python cli.py```
cli.py would download text files from GCP bucket, and then upload the processed files to GCP bucket. You could observe the updates in Cloud Storage - Buckets in your GCP project.
Stop VM instance!
Container 2 TO BE UPDATED

<!-- **Notebooks/Reports**
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations. -->

