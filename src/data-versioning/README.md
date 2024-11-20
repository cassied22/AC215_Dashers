# Tutorial (T7):  Data Versioning Demo

In this tutorial, we will cover data versioning techniques using the cheese app dataset. Everything will be run inside containers using Docker.

## Prerequisites
* Have tha latest Docker installed

## Make sure we do not have any running containers and clear up an unused images
* Run `docker container ls`
* Stop any container that is running
* Run `docker system prune`
* Run `docker image ls`

### Clone the github repository
* Cloned  repository from [here](https://github.com/dlops-io/data-versioning) to your local machine 

Your folder structure should look like this:
```
   |-data-versioning
   |-secrets
```
Download the json file and place inside the secrets folder:
<a href="https://static.us.edusercontent.com/files/mlca0YEYdvkWPNEowJ0o4hOd" download>mega-pipeline.json</a>


### Create a Data Store folder in GCS Bucket
- Go to `https://console.cloud.google.com/storage/browser`
- Go to the bucket `cheese-app-data-versioning` (REPLACE WITH YOUR BUCKET NAME)
- Create a folder `dvc_store` inside the bucket
- Create a folder `images` inside the bucket (This is where we will store the images that need to be versioned)

## Run DVC Container
We will be using [DVC](https://dvc.org/) as our data versioning tool. DVC (Data Version Control) is an open-source, Git-based data science tool. It applies version control to machine learning development, make your repo the backbone of your project.

### Setup DVC Container Parameters
In order for the DVC container to connect to our GCS Bucket open the file `docker-shell.sh` and edit some of the values to match your setup
```
export GCS_BUCKET_NAME="cheese-app-data-versioning" [REPLACE WITH YOUR BUCKET NAME]
export GCP_PROJECT="ac215-project" [REPLACE WITH YOUR GCP PROJECT]
export GCP_ZONE="us-central1-a"


```
### Note: Addition of `docker-entrypoint.sh`
Note that we have added a new file called `docker-entrypoint.sh` to our development flow. A `docker-entrypoint.sh` is used to simplify some task when running containers such as:
* Helps with Initialization and Setup: 
   * The entrypoint file is used to perform necessary setup tasks when the container starts. 
   * It is a way to ensure that certain operations occur every time the container runs, regardless of the command used to start it.
* Helps with Dynamic Configuration:
   * It allows for dynamic configuration of the container environment based on runtime variables or mounted volumes. 
   * This is more flexible than hardcoding everything into the Dockerfile.

For this container we need to:
* Mount a GCS bucket to a volume mount in the container
* We then mount the "images" folder in the bucket mount to the "/app/cheese_dataset" folder

### Run `docker-shell.sh`
- Make sure you are inside the `data-versioning` folder and open a terminal at this location
- Run `sh docker-shell.sh`  


### Version Data using DVC
In this step we will start tracking the dataset using DVC

#### Initialize Data Registry
In this step we create a data registry using DVC
`dvc init`

#### Add Remote Registry to GCS Bucket (For Data)
`dvc remote add -d cheese_dataset gs://cheese-app-data-versioning/dvc_store`

#### Add the dataset to registry
`dvc add cheese_dataset`

#### Push to Remote Registry
`dvc push`

You can go to your GCS Bucket folder `dvs_store` to view the tracking files


#### Update Git to track DVC 
Run this outside the container. 
- First run git status `git status`
- Add changes `git add .`
- Commit changes `git commit -m 'dataset updates...'`
- Add a dataset tag `git tag -a 'dataset_v20' -m 'tag dataset'`
- Push changes `git push --atomic origin main dataset_v20`


### Download Data to view version
In this Step we will use Colab to view various version of the dataset
- Open [Colab Notebook](https://colab.research.google.com/drive/1RRQ1SlHq5lKK76R8LoQdi5LjCnND3jTq?usp=sharing)
- Follow instruction in the Colab Notebook

## Make changes to data

### Upload images
- Upload a few more images to the `images` folder in your bucket (We are simulating some change in data)

#### Add the dataset (changes) to registry
`dvc add cheese_dataset`

#### Push to Remote Registry
`dvc push`

#### Update Git to track DVC changes (again remember this should be done outside the container)
- First run git status `git status`
- Add changes `git add .`
- Commit changes `git commit -m 'dataset updates...'`
- Add a dataset tag `git tag -a 'dataset_v21' -m 'tag dataset'`
- Push changes `git push --atomic origin main dataset_v21`


### Download Data to view version
In this Step we will use Colab to view the new version of the dataset
- Open [Colab Notebook](https://colab.research.google.com/drive/1RRQ1SlHq5lKK76R8LoQdi5LjCnND3jTq?usp=sharing)
- Follow instruction in the Colab Notebook to view `dataset_v21`


### 🎉 Congratulations we just setup and tested data versioning using DVC

## Docker Cleanup
To make sure we do not have any running containers and clear up an unused images
* Run `docker container ls`
* Stop any container that is running
* Run `docker system prune`
* Run `docker image ls`
