import os
import argparse
import pandas as pd
import json
import time
import glob
from sklearn.model_selection import train_test_split
from google.cloud import storage
import zipfile

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
OUTPUT_FOLDER = "data"
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]



raw_folder = "raw_data"
clean_folder = "clean_data"
training_data_folder = "training_data"


def create_preparation_qa(row):
    title = row['title']
    ingredients = row['NER']
    directions = row['directions']

    # Create the specific question-answer pair
    qa_pair = {
        'question': f"Can you give me a recipe using these ingredients: {ingredients}?",
        'answer': f"With those ingredients, we can make a {title}! Here are the step-by-step instructions: {directions}"
    }
    return qa_pair

def prepare():
    print("Preparing dataset for training")

    # Download preparation_qa.csv from GCP bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    csv_file_path = os.path.join(OUTPUT_FOLDER, "preparation_qa.csv")
    blob = bucket.blob("training_data/preparation_qa.csv")
    print("Downloading preparation_qa.csv from GCP bucket...")
    blob.download_to_filename(csv_file_path)

    # Read and process the dataset
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    df = df[['question', 'answer']]
    df['text'] = "human: " + df['question'] + "\n" + "bot: " + df['answer']
    df["contents"] = df.apply(
        lambda row: [
            {"role": "user", "parts": [{"text": row["question"]}]},
            {"role": "model", "parts": [{"text": row["answer"]}]}
        ], axis=1
    )

    # Split data into train and test sets
    df_train, df_test = train_test_split(df, test_size=0.1, random_state=42)
    df_test = df_test[:256]  # Limit test set to 256 examples

    # Save to CSV
    df_train[['text']].to_csv(os.path.join(OUTPUT_FOLDER, "train.csv"), index=False)
    df_test[['text']].to_csv(os.path.join(OUTPUT_FOLDER, "test.csv"), index=False)

    # Save to JSONL
    with open(os.path.join(OUTPUT_FOLDER, "train.jsonl"), "w") as json_file:
        json_file.write(df_train[['contents']].to_json(orient='records', lines=True))
    with open(os.path.join(OUTPUT_FOLDER, "test.jsonl"), "w") as json_file:
        json_file.write(df_test[['contents']].to_json(orient='records', lines=True))

    print("Data preparation complete. Files saved in JSONL and CSV formats.")


def upload():
    print("Uploading processed files to GCP bucket")

    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    # Find all processed files
    data_files = glob.glob(os.path.join(OUTPUT_FOLDER, "*.jsonl")) + glob.glob(os.path.join(OUTPUT_FOLDER, "*.csv"))
    data_files.sort()

    # Upload files
    for data_file in data_files:
        filename = os.path.basename(data_file)
        destination_blob_name = os.path.join("llm_training_data", filename)
        blob = bucket.blob(destination_blob_name)
        print(f"Uploading {data_file} to {destination_blob_name}...")
        blob.upload_from_filename(data_file)

    print("Upload complete.")

def main(args=None):

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(GCS_BUCKET_NAME)

    # Make dirs
    os.makedirs("/persistent", exist_ok=True)

    if args.clean:
        print("Cleaning dataset")

        os.makedirs(raw_folder, exist_ok=True)

        # Download raw_data folder from GCP bucket
        raw_csv_path = os.path.join(raw_folder, "recipe_raw.csv")
        blob = bucket.blob("raw_data/recipe_raw.csv")
        print("Downloading raw_data.csv from GCP bucket...")
        blob.download_to_filename(raw_csv_path)

        # Perform cleaning operations
        raw_csv_path = os.path.join(raw_folder, "recipe_raw.csv")
        recipe = pd.read_csv(raw_csv_path)
        recipe_cleaned = recipe.drop_duplicates().dropna()
        recipe_cleaned = recipe_cleaned[recipe_cleaned['NER'].apply(lambda x: x != '[]')]
        recipe_cleaned_5000 = recipe_cleaned.head(5000)

        # Save the cleaned dataset
        clean_csv_path = os.path.join(clean_folder, "recipe_cleaned.csv")
        os.makedirs(clean_folder, exist_ok=True)
        recipe_cleaned_5000.to_csv(clean_csv_path, index=False)

        # Generate QA pairs
        preparation_qa_data = recipe_cleaned_5000.apply(create_preparation_qa, axis=1)
        preparation_qa_df = pd.DataFrame(preparation_qa_data.tolist())

        # Save QA pairs
        training_data_csv = os.path.join(training_data_folder, "preparation_qa.csv")
        os.makedirs(training_data_folder, exist_ok=True)
        preparation_qa_df.to_csv(training_data_csv, index=False)

        # Upload cleaned data
        blob = bucket.blob("clean_data/recipe_cleaned.csv")
        print("Uploading cleaned data to GCP bucket...")
        blob.upload_from_filename(clean_csv_path)

        # Upload training data
        blob = bucket.blob("training_data/preparation_qa.csv")
        print("Uploading preparation QA data to GCP bucket...")
        blob.upload_from_filename(training_data_csv)

    if args.prepare:
        print("Prepare dataset for training")
        prepare()
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    parser = argparse.ArgumentParser(description="Data Processor CLI")

    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Whether or not to clean the dataset and create QA pairs",
    )

    parser.add_argument(
        "-p",
        "--prepare",
        action="store_true",
        help="Prepare dataset for training.",
    )

    args = parser.parse_args()

    main(args)
