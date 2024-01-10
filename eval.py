import json
import base64
import requests
from dotenv import load_dotenv
import os

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

tasks_config_path = 'tasks_config.jsonl'

config = []
with open(tasks_config_path, 'r') as file:
    for line in file:
        json_object = json.loads(line)
        config.append(json_object)

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

for conf in config:
  prompt_image = f'Tasks/{conf["id"]}/image/{conf["id"]}.png'
  output_image_dir = f'autotest/GPT4V_{conf["id"]}.jpg'
  base64_image = encode_image(prompt_image)
  output_image = encode_image(output_image_dir)
  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Are these two showing a similar pattern?, only Yes or No."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{output_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 30
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  response_text = response.json()["choices"][0]["message"]["content"]
  with open(f'autotest/gpt4v_eval_yn/{conf["id"]}.txt', "w+") as f:
    f.write(response_text)