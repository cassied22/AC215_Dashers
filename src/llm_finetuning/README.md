# LLM Fine-tuning Process

## Training Data

The training data was generated and processed from raw recipe data[https://eightportions.com/datasets/Recipes/#fn:1]. The original dataset consisted of recipes with titles, ingredients, and preparation directions. The preprocessing steps involved:

1. **Data Cleaning**:
   - Removed duplicates and null values.
   - Selected the first 5000 rows of clean data.

2. **Question-Answer Pair Creation**:
   - Generated question-answer pairs by creating questions such as "How do you prepare [recipe title] using these ingredients: [ingredients ]?" and setting the corresponding recipe directions as the answer.
   - Example Question-Answer Pair:
      - Question: "How do you prepare 'Jewell Ball'S Chicken' using these ingredients: [""1 small jar chipped beef, cut up"", ""4 boned chicken breasts"", ""1 can cream of mushroom soup"", ""1 carton sour cream""]?"
      - Answer: "Place chipped beef on bottom of baking dish. Place chicken on top of beef. Mix soup and cream together; pour over chicken. Bake, uncovered, at 275° for 3 hours."
   - The generated question-answer data is saved as a csv file and uploaded it to a private Google Cloud Bucket. It is tracked by DVC.

3. **Data Split**:
   - Split the data into training and test sets using a 90/10 split ratio, ensuring that 10% of the dataset (maximum 256 examples) was held out for testing.

4. **File Formats**:
   - Saved the training and test sets as CSV files for review (`train.csv` and `test.csv`).
   - Additionally, saved the data in JSONL format (`train.jsonl` and `test.jsonl`) for uploading to Vertex AI and used in the fine-tuning process.


## Training Details
The fine-tuning process was executed on Google Cloud Platform (GCP) using Vertex AI.
I finetuning 2 models using the configurations/hyperparameters detailed below, and the picture recording training progress is saved in `./image` folder as `training-img1.png` and `training-img2.png`

### Model 1: food-planner-finetuned-v1
generation_config = {
    "max_output_tokens": 3000,
    "temperature": 0.75,
    "top_p": 0.95,
}
hyperparameter= {
        source_model='gemini-1.5-flash-002',
        epochs=3,
        adapter_size=4,
        learning_rate_multiplier=1.0,
        tuned_model_display_name="food-planner-finetuned-v1"
}


From the training image of model 1, we observed that both training and validation losses are decreasing steadily, which suggest that the model might benefit from additional epochs. Therefore, for the second trial, we increase number of epochs to 4 and also slightly decrease the learning rate to 0.9 to avoid overfitting.


### Model 2: food-planner-finetuned-v2
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.75,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}
hyperparameter= {
        source_model='gemini-1.5-flash-002',
        epochs=4,
        adapter_size=4,
        learning_rate_multiplier=0.9,
        tuned_model_display_name="food-planner-finetuned-v1"
}
