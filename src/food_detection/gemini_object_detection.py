"""Food detection using Google's Gemini Vision API."""
import os

import google.generativeai as genai

from PIL import Image


def setup_gemini():
    """Setup Gemini API."""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        raise Exception(f"Failed to setup Gemini: {str(e)}")


def detect_objects(image_file):
    """Detect food items in an image using Gemini Vision."""
    try:
        model = setup_gemini()

        # Load and prepare the image
        if hasattr(image_file, "read"):
            # Reset file pointer if it's been read
            image_file.seek(0)
            image = Image.open(image_file)
        else:
            image = Image.open(image_file)

        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Define the prompt
        prompt = """
        Analyze this image and list all visible food items and ingredients.
        Format your response as a comma-separated list of ingredients.
        Include only the ingredient names, no additional text.
        Example format: apple, banana, flour, sugar
        """

        # Pass content as a list with both text and image
        response = model.generate_content(
            [prompt, image],
            generation_config={"temperature": 0.1, "top_p": 0.8, "top_k": 40},
        )

        if response and response.text:
            # Clean and process the response
            ingredients = [
                item.strip()
                for item in response.text.split(",")
                if item.strip() and not item.strip().startswith("- ")
            ]
            return [ing for ing in ingredients if ing]  # Remove empty strings

        return []

    except Exception as e:
        print(f"Debug - Error in detect_objects: {str(e)}")
        raise Exception(f"Food detection failed: {str(e)}")


def get_ingredient_details(ingredients):
    """Get detailed information about ingredients."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        For these ingredients: {', '.join(ingredients)}
        Provide a JSON object with the following structure:
        {{
            "recipes": ["recipe1", "recipe2", "recipe3"],
            "shelf_life": "information about shelf life",
            "storage": "storage recommendations"
        }}
        Keep the response concise and focused on common kitchen knowledge.
        """

        response = model.generate_content(
            prompt, generation_config={"temperature": 0.1, "top_p": 0.8, "top_k": 40}
        )

        if response and response.text:
            import json

            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {
                    "recipes": ["Recipe information not available"],
                    "shelf_life": "Information not available",
                    "storage": "Information not available",
                }

        return None

    except Exception as e:
        raise Exception(f"Failed to get ingredient details: {str(e)}")


def test_model_availability():
    """Test if the model is available and working."""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("List three common kitchen ingredients.")
        if response and response.text:
            return "Model test successful: Gemini 1.5 Flash is working"
        return "Model test failed: no response received"
    except Exception as e:
        return f"Model test failed: {str(e)}"
