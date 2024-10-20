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

**Data Pipeline Containers**

1. One container prepares data for the RAG model, including tasks such as chunking, embedding, and populating the vector database.

## Data Pipeline Overview

1. **`src/datapipeline/cli_rag.py`**
   This script handles preprocessing on our 2.29 GB dataset in the `input-datasets` folder. It does data cleaning and feature selection to enable faster iteration during processing. The preprocessed dataset is now reduced to 676 MB and stored on GCS. The `outputs` folder is a temperary path where the local copy of the vector database is stored. 
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

