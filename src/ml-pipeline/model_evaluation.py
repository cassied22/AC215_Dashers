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

# Function to extract ingredients based on the corrected pattern
def extract_ingredients_corrected(question):
    # Look for ingredients after "using these ingredients:"
    match = re.search(r'using these ingredients:\s*\[(.*?)\]', question, re.IGNORECASE)
    if match:
        # Split ingredients within the brackets and clean up
        ingredients = re.findall(r'"(.*?)"', match.group(1))
        return [ingredient.strip().lower() for ingredient in ingredients]
    return []


def calculate_ingredient_match(question, answer):
    """
    Calculate the percentage of ingredients mentioned in the recipe answer.

    Args:
        question (str): The question containing the list of ingredients.
        answer (str): The recipe text.

    Returns:
        float: The percentage of ingredients mentioned in the recipe.
    """
    # Extract ingredients from the question
    ingredients = extract_ingredients_corrected(question)
    # Convert the recipe text to lowercase for case-insensitive matching
    recipe_text = answer.lower()
    if not ingredients:
        return 0
    # Count how many ingredients appear in the recipe text
    matched_ingredients = [ing for ing in ingredients if ing in recipe_text]
    # Calculate the percentage of ingredients found
    return len(matched_ingredients) / len(ingredients) * 100


def comupute_valid_pair_percentages(data, threshold=25):
     # Calculate the percentage of rows with more than 25% of ingredients mentioned in the recipe 
    over_threshold_percent = (data['match_percentage'] >= threshold).mean() * 100
    return over_threshold_percent


def get_valid_percentages(data):
    # Given data consisting of question/answer pair, calculate the pertentage of valid receipes generated  
    # valid recipes are defined by the recipe which contains more than 50% of ingrendients mentioned in the prompt
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
    data.loc[:, 'answer'] = data['question'].apply(lambda question: generative_model.generate_content(
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
