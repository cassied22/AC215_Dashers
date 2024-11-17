import google.generativeai as genai
import sys
import os

def identify_food_gemini(image_path, api_key):
    genai.configure(api_key=api_key)
    myfile = genai.upload_file(image_path)

    model = genai.GenerativeModel("gemini-1.5-flash")
    result = model.generate_content(
        [myfile, "\n\n", "Identify the list of food items shown in this image. (Example Output1: ['pear','apple','salt', ...]). If no food is found in the image, output ['None']. (Example Output2: ['None'])"]
    )
    return result.text

def main():
    if len(sys.argv) != 2:
        print("Usage: python food_item_identifier.py <image_path>")
        sys.exit(1)
    else:
        image_path = sys.argv[1]
        api_key = os.getenv("GEMINI_API_KEY")

        result = identify_food_gemini(image_path, api_key)
        print(result)


if __name__ == "__main__":
    main()