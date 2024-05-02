import os
import time
import base64

from openai import OpenAI

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

class GPTModel:
  def __init__(self, api_key, patience=1, sleep_time=1) -> None:
    self.patience = patience
    self.sleep_time = sleep_time
    self.api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }
    self.client = OpenAI(default_headers=headers)
    self.model_name = "gpt-4-turbo"

  def get_response(self, system_message, user_message, base_image, result_image):
    messages = [
      {"role": "system", "content": system_message},
      {"role": "user", "content": [{"type": "text", "text": user_message}]}
    ]
    patience = self.patience
    
    while patience > 0:
      patience -= 1
      try:
        if base_image:
          assert os.path.exists(base_image)
        if result_image:
          assert os.path.exists(result_image)
        if base_image: image1 = encode_image(base_image)
        if result_image: image2 = encode_image(result_image)
        image1_dict = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image1}"}}
        image2_dict = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image2}"}}
        user_dict = messages[1]
        user_dict["content"] += [image1_dict] if base_image else [] 
        user_dict["content"] += [image2_dict] if base_image else [] 
        response = self.client.chat.completions.create(messages=messages, model=self.model_name, max_tokens=1000)
        response = response.choices[0].message.content.strip()
        if response != "" and response != None:
          return response
      except Exception as e:
        print(e)
    
    return ""
