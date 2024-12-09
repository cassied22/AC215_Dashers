from kfp import dsl

# Define a Fine-Tuning Component
def gemini_fine_tune_component(
    project: str,
    location: str,
    train_dataset: str,
    validation_dataset: str,
    tuned_model_display_name: str,
    source_model: str = "gemini-1.5-flash-002"
) -> str:
    import vertexai
    from vertexai.preview.tuning import sft
    import time

    vertexai.init(project=project, location=location)

    print(f"Starting fine-tuning of Gemini model: {source_model}")
    sft_tuning_job = sft.train(
        source_model=source_model,
        train_dataset=train_dataset,
        validation_dataset=validation_dataset,
        epochs=3,  # Adjust epochs as needed
        adapter_size=4,
        learning_rate_multiplier=0.9,
        tuned_model_display_name=tuned_model_display_name,
    )

    while not sft_tuning_job.has_ended:
        time.sleep(60)
        sft_tuning_job.refresh()
        print("Tuning job in progress...")

    print(f"Fine-tuning complete. Model Name: {sft_tuning_job.tuned_model_name}")
    return sft_tuning_job.tuned_model_name


# # Deployment Component
# @dsl.component(
#     base_image="python:3.10",
#     packages_to_install=["google-cloud-aiplatform", "vertexai"]
# )
# def gemini_deploy_component(
#     project: str,
#     location: str,
#     model_name: str,
#     machine_type: str = "n1-standard-4",
#     min_replica_count: int = 1,
#     max_replica_count: int = 1
# ) -> str:
#     from vertexai.generative_models import GenerativeModel
#     vertexai.init(project=project, location=location)

#     print(f"Deploying model: {model_name}")
#     generative_model = GenerativeModel.from_pretrained(model_name)
#     endpoint = generative_model.deploy(
#         machine_type=machine_type,
#         min_replica_count=min_replica_count,
#         max_replica_count=max_replica_count
#     )

#     print(f"Model deployed at endpoint: {endpoint.name}")
#     return endpoint.name


