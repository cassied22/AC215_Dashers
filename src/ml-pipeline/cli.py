"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py
"""

import os
import argparse
import random
import string

import google.cloud.aiplatform as aip
import vertexai
from vertexai.preview.tuning import sft


from data_process import prepare as data_prepare, upload as data_upload, clean as data_clean
from model_training import gemini_fine_tuning
from model_evaluation import evaluate


GCP_PROJECT = os.environ["GCP_PROJECT"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
TRAIN_DATASET = f"gs://food-planner-ml-workflow/llm_training_data/train.jsonl"
VALIDATION_DATASET = "gs://food-planner-ml-workflow/llm_training_data/test.jsonl"
# GCS_PACKAGE_URI = os.environ["GCS_PACKAGE_URI"]
GCP_LOCATION = "us-central1"



def generate_uuid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def run_pipeline():
    print("Running the entire pipeline: Data Processing, Model Training, and Model Evaluation")

    # Step 1: Data processing
    print("Step 1: Cleaning and Preparing Data")
    data_clean()
    data_prepare()
    data_upload()

    job_id = generate_uuid()

    DISPLAY_NAME = "food-planner-" + job_id

    # Step 2: Model training
    print("Step 2: Training the Model")
    tuned_model_name, endpoint_name = gemini_fine_tuning(
        project=GCP_PROJECT,
        location=GCP_LOCATION,
        train_dataset=f"gs://{GCS_BUCKET_NAME}/llm_training_data/train.jsonl",
        validation_dataset=f"gs://{GCS_BUCKET_NAME}/llm_training_data/test.jsonl",
        tuned_model_display_name=DISPLAY_NAME,
    )
    print(f"Model tuned: {tuned_model_name}, Endpoint: {endpoint_name}")

    # Step 3: Model evaluation
    print("Step 3: Evaluating the Model")
    valid_percentage = evaluate(endpoint=endpoint_name)
    print(f"Validation Percentage of Correct Pairs: {valid_percentage:.2f}%")

    print("Pipeline execution complete.")
   
    

def main():
    parser = argparse.ArgumentParser(description="Pipeline CLI for Data Processing, Model Training, and Evaluation")
    
    parser.add_argument(
        "--data_processor",
        action="store_true",
        help="Run data processing steps: clean, prepare, and upload data.",
    )
    parser.add_argument(
        "--model_training",
        action="store_true",
        help="Run the model training process.",
    )
    parser.add_argument(
        "--model_evaluation",
        action="store_true",
        help="Run the model evaluation process.",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Run the entire pipeline: Data Processing, Model Training, and Evaluation.",
    )
    
    args = parser.parse_args()

    if args.data_processor:
        print("Running Data Processor")
        data_clean()
        data_prepare()
        data_upload()

    if args.model_training:
        print("Running Model Training")
        job_id = generate_uuid()

        DISPLAY_NAME = "food-planner-" + job_id
        gemini_fine_tuning(
            project=GCP_PROJECT,
            location=GCP_LOCATION,
            train_dataset=f"gs://{GCS_BUCKET_NAME}/llm_training_data/train.jsonl",
            validation_dataset=f"gs://{GCS_BUCKET_NAME}/llm_training_data/test.jsonl",
            tuned_model_display_name=DISPLAY_NAME,
        )

    if args.model_evaluation:
        print("Running Model Evaluation")
        evaluate()

    if args.pipeline:
        run_pipeline()

if __name__ == "__main__":
    main()