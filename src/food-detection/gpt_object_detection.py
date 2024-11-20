import base64
import requests
import sys
import os
import json

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        sys.exit(1)

def identify_food_gpt(image_path, api_key):
    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Identify the list of food items shown in this image. (Example Output1: ['pear','apple','salt', ...]). If no food is found in the image, output ['None']. (Example Output2: ['None'])"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()['choices'][0]['message']['content']

def main():
    if len(sys.argv) != 2:
        print("Usage: python food_item_identifier.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    api_key_path = os.getenv("OPENAI_API_KEY")
    with open(api_key_path, 'r') as file:
        api_key = json.load(file).get('OPENAI_API_KEY')

    result = identify_food_gpt(image_path, api_key)
    print(result)

if __name__ == "__main__":
    main()