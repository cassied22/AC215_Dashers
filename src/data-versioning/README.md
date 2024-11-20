# Data Versioning 

This folder includes container for data versioning control. We are using DVC for data versioning control. The DVC was chosen because it provides a robust and scalable solution for managing large datasets and machine learning models, which is particularly important for our project as we plan on incorporating larger recipe dataset for future steps. We are tracking only the one version of training data used for fine-tunning LLM (data/recipe_qa.csv, remotely tracked on GCP), and might continue to track more data in the future milestones as needed.

- Run docker container by using:
```chmod +x docker-shell.s```
```sh docker-shell.sh```
