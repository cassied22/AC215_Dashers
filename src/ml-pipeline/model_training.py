# Gemini Fine-Tuning
import vertexai
from vertexai.preview.tuning import sft
import time

def gemini_fine_tuning(
    project: str,
    location: str,
    train_dataset: str,
    validation_dataset: str,
    tuned_model_display_name: str,
    source_model: str = "gemini-1.5-flash-002",
    epochs = 4, 
    adapter_size=4,
    learning_rate_multiplier=0.9,

):

    vertexai.init(project=project, location=location)

    print(f"Starting fine-tuning of Gemini model: {source_model}")
    sft_tuning_job = sft.train(
        source_model=source_model,
        train_dataset=train_dataset,
        validation_dataset=validation_dataset,
        epochs=epochs,  # Adjust epochs as needed
        adapter_size=adapter_size,
        learning_rate_multiplier=learning_rate_multiplier,
        tuned_model_display_name=tuned_model_display_name,
    )

    while not sft_tuning_job.has_ended:
        time.sleep(60)
        sft_tuning_job.refresh()
        print("Tuning job in progress...")

    print(f"Fine-tuning complete. Model Endpoints: {sft_tuning_job.tuned_model_endpoint_name}")
    print(f"Model Name: {sft_tuning_job.tuned_model_name}")
    return sft_tuning_job.tuned_model_name, sft_tuning_job.tuned_model_endpoint_name



