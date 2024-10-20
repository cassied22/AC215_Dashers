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
|   └── Daily Meal Assistant Prototype.pdf
│   └── Statement of Work_Sample.pdf
|   └── Prototype_v2.pdf
└── src
    ├── datapipeline
    │   ├── cli_rag.py
    │   ├── Dockerfile
    │   ├── docker-compose.yml
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── dataloader.py
    │   ├── docker-shell.sh
    │   ├── preprocess_cv.py
    │   ├── requirements.txt
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

Hanqi(Hanna) Zeng(hanqizeng@hsph.harvard.edu)  <br/> 
Chris Wang(ywang3@hsph.harvard.edu)   <br/> 
Selina Qian(jingyun_qian@hsph.harvard.edu) <br/> 
Shiyu Ma(shiyuma@g.harvard.edu)  <br/> 
Cassie Dai(cdai@g.harvard.edu) <br/> 


**Group Name**
Dashers

**Project**
In this project, we aim to develop an app that serves as a personal meal assistant, helping users track their available ingredients, suggest healthy recipes, and recommend nearby restaurants based on user preferences and current inventory. The app will combine advanced AI tools like object detection and large language models (LLMs) to provide tailored meal recommendations and route suggestions for dining out. <br/>

The app pipeline flow is as shown [here](https://github.com/cassied22/AC215_Dashers/blob/milestone2/reports/Prototype_v2.pdf).

### Milestone2 ###

In this milestone, we have the components for data management, including versioning, as well as the computer vision and language models.

**Data**
We gathered a dataset of 2,231,150 recipes including title (dish name), ingredients, directions, retrieved link, source type, and named entity recognition (NER) for food items. The ingredients are listed as an array of strings. The directions are provided as an array of strings, with each string representing a step in the cooking process. The NER data consists of an array of food item names extracted from the recipe. The dataset, approximately 2.29 GB in size, was collected from the following source: https://huggingface.co/datasets/mbien/recipe_nlg. We have stored it in a private Google Cloud Bucket.

**Data Pipeline Containers**

1. One container prepares data for the RAG model, including tasks such as chunking, embedding, and populating the vector database.

## Data Pipeline Overview

1. **`src/datapipeline/cli_rag.py`**
   This script handles preprocessing on our 2.29 GB dataset. It does data cleaning and feature selection to enable faster iteration during processing. The preprocessed dataset is now reduced to XX GB and stored on GCS.
   This script also prepares the necessary data for setting up our vector database. It performs chunking, embedding, and loads the data into a vector database (ChromaDB).

2. **`src/datapipeline/Pipfile`**
   We used the following packages to help with preprocessing:
   - `user-agent requests google-cloud-storage google-generativeai google-cloud-aiplatform pandas langchain llama-index chromadb langchain-community pyarrow`

3. **`src/preprocessing/Dockerfile(s)`**
   Our Dockerfiles follow standard conventions, with the exception of some specific modifications described in the Dockerfile/described below.


## Running Dockerfile
Go to a terminal inside datapipeline
- Run docker container by using:
```sh docker-shell.sh```

## Mock Submission

<br/>
Login GCP, select project id, our ```x-goog-project-id```, start the VM instance.<br/>
Open a GCP terminal, change directory into corresponding folder with Dockerfile. <br/>
Run docker-shell.sh using command: ```sudo sh docker-shell.sh``` <br/>
Inside the container, run preprocessing using command: ```python cli_rag.py```. <br/>
cli_rag.py would run the RAG LLM. You could observe the updates in Cloud Storage - Buckets in your GCP project. <br/>

<!-- **Notebooks/Reports**
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations. -->

