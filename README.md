## Milestone 2

<!-- ```
The files are empty placeholders only. You may adjust this template as appropriate for your project.
Never commit large data files,trained models, personal API Keys/secrets to GitHub
``` -->

#### Project Milestone 2 Organization

```
├── .dvc
│   ├── .gitignore
│   ├── cache
│   │   └── files
│   ├── config
│   ├── config.local
│   └── tmp
│       ├── btime
│       ├── lock
│       ├── rwlock
│       ├── rwlock.lock
│       ├── updater
│       └── updater.lock
├── .dvcignore
├── .git
│   ├── COMMIT_EDITMSG
│   ├── FETCH_HEAD
│   ├── HEAD
│   ├── ORIG_HEAD
│   ├── branches
│   ├── config
│   ├── description
│   ├── hooks
│   ├── index
│   ├── info
│   │   └── exclude
│   ├── logs
│   │   ├── HEAD
│   │   └── refs
│   ├── objects
│   ├── packed-refs
│   └── refs
│       ├── heads
│       ├── remotes
│       └── tags
├── .gitignore
├── LICENSE
├── README.md
├── data
│   ├── recipe_qa.csv
│   └── recipe_qa.csv.dvc
├── notebooks
│   ├── Object_detection_documentation.md
│   ├── container.ipynb
│   ├── dvc_retrieval.ipynb
│   ├── eda.ipynb
│   ├── fig_container
│   │   └── rag_container.png
│   ├── fig_llm_performance
│   │   ├── raw-rag3-1.png
│   │   ├── raw_rag1-1.png
│   │   ├── raw_rag1-2.png
│   │   ├── raw_rag1-3.png
│   │   ├── raw_rag2-1.png
│   │   ├── raw_rag2-2.png
│   │   └── raw_rag3-2.png
│   ├── food
│   │   ├── food1.jpg
│   │   ├── food1_gemini.png
│   │   ├── food1_gpt.png
│   │   ├── food1_mediapipe.png
│   │   ├── food1_yolov8.png
│   │   ├── food2.png
│   │   ├── food2_gemini.png
│   │   ├── food2_gpt.png
│   │   ├── food2_mediapipe.png
│   │   ├── food2_yolov8.png
│   │   ├── food3.jpg
│   │   ├── food3_gemini.png
│   │   ├── food3_gpt.png
│   │   ├── food3_mediapipe.png
│   │   └── food3_yolov8.png
│   └── llm_performance.ipynb
├── references
│   └── .gitkeep
├── reports
│   ├── Daily Meal Assistant Prototype.pdf
│   ├── Prototype_v2.pdf
│   └── Statement of Work_Sample.pdf
└── src
    ├── data-versioning
    │   ├── .gitignore
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── README.md
    │   ├── docker-entrypoint.sh
    │   └── docker-shell.sh
    ├── datapipeline
    │   ├── .gitignore
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli_rag.py
    │   ├── dataloader.py
    │   ├── docker-compose.yml
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    │   ├── input-datasets
    │   ├── outputs
    │   ├── preprocess_cv.py
    │   └── requirements.txt
    ├── food-detection
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── data
    │   ├── docker-compose.yml
    │   ├── docker-shell.sh
    │   ├── gemini-object-detection.py
    │   ├── gpt-object-detection.py
    │   └── requirements.txt
    ├── llm_finetuning
    │   ├── .gitignore
    │   ├── README.md
    │   ├── dataset-creator
    │   ├── env.dev
    │   ├── gemini-finetuner
    │   └── images
    ├── models
    │   ├── Dockerfile
    │   ├── docker-shell.sh
    │   ├── infer_model.py
    │   ├── model_rag.py
    │   └── train_model.py
    └── secrets
        └── .gitkeep
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


**Containers**

1. **Data Pipeline Container** (https://github.com/cassied22/AC215_Dashers/tree/milestone2/src/datapipeline): The container prepares data for LLM with RAG, including tasks such as chunking, embedding, and populating the vector database, and output recommended recipe. 
2. **Date Versioning Container** (https://github.com/cassied22/AC215_Dashers/tree/milestone2/src/data-versioning) :The container controls data versioning using DVC. The DVC was chosen because it provides a robust and scalable solution for managing large datasets and machine learning models, which is particularly important for our project as we plan on incorporating larger recipe dataset for future steps. (with .dvc stored here:
https://github.com/cassied22/AC215_Dashers/tree/milestone2/.dvc)
3. **Object  Container** (https://github.com/cassied22/AC215_Dashers/tree/milestone2/src/food-detection) :The container includes all codes conducting the object detection functionality: given a picture, output list of detected food.
4. **LLM Finetuning** (https://github.com/cassied22/AC215_Dashers/tree/milestone2/src/llm_finetuning) :The container performs LLM finetuning task.


## Instructions for Running Containers
Go to a terminal inside each folder
- Build docker image by using:
```sudo docker build -t XXX -f Dockerfile .```
- Run docker container by using:
```chmod +x docker-shell.s```
```sh docker-shell.sh```
```sh docker-shell.sh```


## Documentations
1. **Data Version Control**: (https://github.com/cassied22/AC215_Dashers/blob/milestone2/notebooks/dvc_tracked_history_logs.png; https://github.com/cassied22/AC215_Dashers/blob/milestone2/notebooks/dvc_retrieval.ipynb) We control data versions using DVC. The DVC was chosen because it provides a robust and scalable solution for managing large datasets and machine learning models, which is particularly important for our project as we plan on incorporating larger recipe dataset for future steps. Currently we are tracking only the one version of training data used for fine-tunning LLM (data/recipe_qa.csv, remotely tracked on GCP), and plan on tracking more data in the future milestones as needed.  
2. **fine-tuning process**：https://github.com/cassied22/AC215_Dashers/blob/milestone2/src/llm_finetuning/README.md
3. **Experiment logs for llm**：(https://github.com/cassied22/AC215_Dashers/blob/milestone2/notebooks/llm_performance.ipynb)
4. **Experiment logs for object detection**：(https://github.com/cassied22/AC215_Dashers/blob/milestone2/notebooks/Object_detection_documentation.md)
5. **Application mock-up**：Front end: https://github.com/cassied22/AC215_Dashers/blob/milestone2/notebooks/front-end.txt; backend interaction: https://github.com/cassied22/AC215_Dashers/blob/milestone2/reports/Prototype_v2.pdf
6. **Running Docker** https://github.com/cassied22/AC215_Dashers/blob/milestone2/notebooks/fig_container/rag_container.png

<!-- **Notebooks/Reports**
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations. -->
## Data Pipeline Overview

1. **`src/datapipeline/cli_rag.py`**
   This script handles preprocessing on our 2.29 GB dataset in the `input-datasets` folder. It does data cleaning and feature selection to enable faster iteration during processing. The preprocessed dataset is now reduced to 676 MB and stored on GCS. The `outputs` folder is a temperary path where the local copy of the vector database is stored. 
   This script also prepares the necessary data for setting up our vector database. It performs chunking, embedding, and loads the data into a vector database (ChromaDB).

2. **`src/datapipeline/Pipfile`**
   We used the following packages to help with preprocessing:
   - `user-agent requests google-cloud-storage google-generativeai google-cloud-aiplatform pandas langchain llama-index chromadb langchain-community pyarrow`

3. **`src/preprocessing/Dockerfile(s)`**
   Our Dockerfiles follow standard conventions, with the exception of some specific modifications described in the Dockerfile/described below.

## Mock Submission

<br/>
Login GCP, select project id, our "x-goog-project-id", start the VM instance.<br/>
Open a GCP terminal, change directory into corresponding folder with Dockerfile. <br/>
Run docker-shell.sh using command: <br/>

```sudo sh docker-shell.sh``` 
Inside the container, run preprocessing using command: ```python cli_rag.py```. <br/>
cli_rag.py would run the RAG LLM. You could observe the updates in Cloud Storage - Buckets in your GCP project. <br/>

<!-- **Notebooks/Reports**
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations. -->

