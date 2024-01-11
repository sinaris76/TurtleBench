import json
import base64
import requests
from dotenv import load_dotenv
import os
from sandbox import execute_combined_code
from utils.code_analysis import find_screen_variable_name
import subprocess

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


# tasks_config_path = 'tasks_config.jsonl'
tasks_config_path = 'dataset.jsonl'
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
  # prompt_file = f'Tasks/{conf["id"]}/QA/text/q1.txt'
  # prompt_text = open(prompt_file, 'r').read()
  # prompt_image = f'Tasks/{conf["id"]}/image/{conf["id"]}.png'
  prompt_text = conf['query']
  prompt_base_image = conf['base_shape']
  base64_image = encode_image(prompt_base_image)
  question_number = conf['question_number']

  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt_text + "\n say nothing more, only give the code \n set the speed at the highest and hide the turtle"
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
    "max_tokens": 1000
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  response_text = response.json()["choices"][0]["message"]["content"]
  with open(f'gpt4v_responses/{conf["id"]}_{question_number}_response.txt', "w+") as f:
    f.write(response_text)
  clean_code = response_text.strip('`').replace('python', '', 1).replace('turtle.done()', '')\
    .replace('.mainloop()', '').replace('.exitonclick()', '')
  svn = find_screen_variable_name(clean_code)
  subprocess
  code = execute_combined_code(clean_code, 'GPT4V', conf["id"], question_number, svn)
  file_path = 'file_path_{}.py'.format(conf["id"])
  with open(file_path, 'w') as file:
    file.write(code)
  completed_process = subprocess.run(['python', file_path])
  if completed_process.returncode == 0:
    os.remove(file_path)
  else:
    print("Process failed, return code:", completed_process.returncode)

  