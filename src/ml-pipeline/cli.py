"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py
"""

import os
import argparse
import random
import string
from kfp import dsl
from kfp import compiler
import google.cloud.aiplatform as aip
import vertexai
from vertexai.preview.tuning import sft


from model import gemini_fine_tune_component, gemini_deploy_component


GCP_PROJECT = os.environ["GCP_PROJECT"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
BUCKET_URI = f"gs://{GCS_BUCKET_NAME}"
PIPELINE_ROOT = f"{BUCKET_URI}/pipeline_root/root"
TRAIN_DATASET = f"gs://food-planner-ml-workflow/llm_training_data/train.jsonl"
VALIDATION_DATASET = "gs://food-planner-ml-workflow/llm_training_data/test.jsonl"
GCS_SERVICE_ACCOUNT = os.environ["GCS_SERVICE_ACCOUNT"]
# GCS_PACKAGE_URI = os.environ["GCS_PACKAGE_URI"]
GCP_REGION = os.environ["GCP_REGION"]
GCP_LOCATION = "us-central1"


# # Read the docker tag file
# with open(".docker-tag-ml") as f:
#     tag = f.read()

# tag = tag.strip()

# print("Tag>>", tag, "<<")


# DATA_PROCESSOR_IMAGE = f"gcr.io/{GCP_PROJECT}/cheese-app-data-processor:{tag}"


def generate_uuid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))



def data_processor():
    print("data_processor()")

    # Define a Container Component for data processor
    @dsl.container_component
    def data_processor():
        container_spec = dsl.ContainerSpec(
            image=DATA_PROCESSOR_IMAGE,
            command=[],
            args=[
                "cli.py",
                "--clean",
                "--prepare",
            ],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def data_processor_pipeline():
        data_processor()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        data_processor_pipeline, package_path="data_processor.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "food-planner-data-processor-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="data_processor.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def model_training():
    print("Running Model Training...")

    model_name = gemini_fine_tune_component(
        project=GCP_PROJECT,
        location=GCP_LOCATION,
        train_dataset=TRAIN_DATASET,
        validation_dataset=VALIDATION_DATASET,
        tuned_model_display_name=f"gemini-finetuned-{generate_uuid()}",
    )

    print(f"Fine-tuned model: {model_name}")


# def model_deploy():
#     print("Running Model Deployment...")

#     @dsl.pipeline
#     def model_deploy_pipeline():
#         gemini_deploy_component(
#             project=GCP_PROJECT,
#             location=GCP_LOCATION,
#             model_name="gemini-finetuned-model",  # Update with the actual model name
#         )

#     # Compile and submit pipeline
#     compiler.Compiler().compile(
#         pipeline_func=model_deploy_pipeline,
#         package_path="model_deploy.yaml",
#     )
#     aip.init(project=GCP_PROJECT, staging_bucket=f"gs://{GCS_BUCKET_NAME}")
#     job_id = generate_uuid()
#     DISPLAY_NAME = f"model-deploy-{job_id}"
#     job = aip.PipelineJob(
#         display_name=DISPLAY_NAME,
#         template_path="model_deploy.yaml",
#         pipeline_root=PIPELINE_ROOT,
#         enable_caching=False,
#     )
#     job.run(service_account=GCS_SERVICE_ACCOUNT)

def pipeline():
    print("Running Entire Pipeline...")

    @dsl.pipeline
    def full_pipeline():
        data_processor_task = dsl.ContainerOp(
            name="data-processor",
            image=DATA_PROCESSOR_IMAGE,
            command=[],
            arguments=["cli.py", "--clean", "--prepare"],
        )

        model_training_task = gemini_fine_tune_component(
            project=GCP_PROJECT,
            location=GCP_LOCATION,
            train_dataset=TRAIN_DATASET,
            validation_dataset=VALIDATION_DATASET,
            tuned_model_display_name=f"gemini-finetuned-{generate_uuid()}",
        ).after(data_processor_task)

        # gemini_deploy_component(
        #     project=GCP_PROJECT,
        #     location=GCP_LOCATION,
        #     model_name=model_training_task.output,
        # ).after(model_training_task)

    # Compile and submit pipeline
    compiler.Compiler().compile(
        pipeline_func=full_pipeline,
        package_path="pipeline.yaml",
    )
    aip.init(project=GCP_PROJECT, staging_bucket=f"gs://{GCS_BUCKET_NAME}")
    job_id = generate_uuid()
    DISPLAY_NAME = f"ml-pipeline-{job_id}"
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="pipeline.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )
    job.run(service_account=GCS_SERVICE_ACCOUNT)

def main(args):
    if args.data_processor:
        data_processor()
    elif args.model_training:
        model_training()
    elif args.model_deploy:
        model_deploy()
    elif args.pipeline:
        pipeline()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ML Workflow CLI")
    parser.add_argument("--data_processor", action="store_true", help="Run Data Processor")
    parser.add_argument("--model_training", action="store_true", help="Run Model Training")
    parser.add_argument("--model_deploy", action="store_true", help="Run Model Deployment")
    parser.add_argument("--pipeline", action="store_true", help="Run the Entire Pipeline")
    args = parser.parse_args()
    main(args)
