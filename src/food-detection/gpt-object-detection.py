import base64
import requests
import sys
import os

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
            "text": "Give me the name of food items shown in this image. Not a full sentense."
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
    api_key = os.getenv("OPENAI_API_KEY")

    result = identify_food_gpt(image_path, api_key)
    print(result)

if __name__ == "__main__":
    main()