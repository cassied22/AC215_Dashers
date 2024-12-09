import os
import pandas as pd
import re
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, GenerationConfig

# GCP setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
OUTPUT_FOLDER = "data"
TESTING_DATA_FOLDER = "testing_data"
TEST_FILE_PATH = os.path.join(TESTING_DATA_FOLDER, "test_qa.csv")
GENERATION_CONFIG = GenerationConfig(
    max_output_tokens=3000,
    temperature=0.75,
    top_p=0.95,
)
# def chat():
#     print("chat()")
#     # Get the model endpoint from Vertex AI: https://console.cloud.google.com/vertex-ai/studio/tuning?project=ac215-project
#     #MODEL_ENDPOINT = "projects/129349313346/locations/us-central1/endpoints/810191635601162240"
#     #MODEL_ENDPOINT = "projects/129349313346/locations/us-central1/endpoints/5584851665544019968"
#     # MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/9072590509779714048" # Finetuned model

#         # MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/9072590509779714048" # Finetuned model
#     # MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/2727018634814685184"
#     # MODEL_ENDPOINT ="projects/978082269307/locations/us-central1/endpoints/8362147668562018304"
#     MODEL_ENDPOINT = "projects/978082269307/locations/us-central1/endpoints/2539828979209076736"
#     print(MODEL_ENDPOINT)
    
#     generative_model = GenerativeModel(MODEL_ENDPOINT)

#     query = """Can you give me a recipe using these ingredients: [""margarine"", ""white sugar"", ""brown sugar"", ""chunky peanut butter"", ""vanilla"", ""eggs"", ""oats"", ""soda"", ""chocolate chips""]?"""
#     print("query: ",query)
#     response = generative_model.generate_content(
#         [query],  # Input prompt
#         generation_config=GENERATION_CONFIG,  # Configuration settings
#         stream=False,  # Enable streaming for responses
#     )
#     generated_text = response.text
#     print("Fine-tuned LLM Response:", generated_text)
     

# def main(args=None):
#     print("CLI Arguments:", args)
#     if args.train:
#         train()
    
#     if args.chat:
#         chat()

# Function to extract ingredients based on the corrected pattern
def extract_ingredients_corrected(question):
    match = re.search(r'using these ingredients:\s*\[(.*?)\]', question, re.IGNORECASE)
    if match:
        ingredients = re.findall(r'"(.*?)"', match.group(1))
        return [ingredient.strip().lower() for ingredient in ingredients]
    return []


def calculate_ingredient_match(question, answer):
    ingredients = extract_ingredients_corrected(question)
    recipe_text = answer.lower()
    if not ingredients:
        return 0
    matched_ingredients = [ing for ing in ingredients if ing in recipe_text]
    return len(matched_ingredients) / len(ingredients) * 100


def comupute_valid_pair_percentages(data, threshold=25):
    over_threshold_percent = (data['match_percentage'] >= threshold).mean() * 100
    return over_threshold_percent


def get_valid_percentages(data):
    data['ingredients'] = data['question'].apply(extract_ingredients_corrected)
    data['match_percentage'] = data.apply(lambda row: calculate_ingredient_match(row['question'], row['answer']), axis=1)
    return comupute_valid_pair_percentages(data)


def evaluate(endpoint="projects/978082269307/locations/us-central1/endpoints/486187549128130560"):
    # Download the test file from GCP
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    print(f"Downloading {TEST_FILE_PATH} from GCP bucket...")
    blob = bucket.blob("testing_data/test_qa.csv")
    os.makedirs(TESTING_DATA_FOLDER, exist_ok=True)
    blob.download_to_filename(TEST_FILE_PATH)

    # Read the test dataset
    try:
        data = pd.read_csv(TEST_FILE_PATH)
        data = data.head(10)
    except Exception as e:
        print(f"Error reading the test dataset: {e}")
        return

    # Initialize the model
    print("Initializing the Generative Model...")
    generative_model = GenerativeModel(endpoint)

    # Generate answers for each question
    print("Generating answers...")
    data['answer'] = data['question'].apply(lambda question: generative_model.generate_content(
        [question],
        generation_config=GENERATION_CONFIG,
        stream=False
    ).text)

    # Compute valid pair percentages
    valid_percentage = get_valid_percentages(data)

    print(f"Percentage of valid question-answer pairs: {valid_percentage:.2f}%")
    return valid_percentage


if __name__ == "__main__":
    evaluate()
