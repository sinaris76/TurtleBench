import os
import time
import PIL

import google.generativeai as genai


def verify_response(response):
    if isinstance(response, str):
        response = response.strip() 
    if response == "" or response == None:
        return False
    if "Response Error" in response:
        # print("Response Error")
        return False
    return True

class GeminiModel:
  def __init__(self, api_key, patience=15, sleep_time=1) -> None:
    self.patience = patience
    self.sleep_time = sleep_time
    genai.configure(api_key=api_key)
    self.model = genai.GenerativeModel('gemini-1.5-flash')
  
  def get_response(self, system_message, user_prompt, base_image, result_image, few_shot=False):
    if not few_shot:
      text_input = system_message + '\n' * 3 + user_prompt
    else:
      text_input = system_message 

    patience = self.patience
    while patience > 0:
      patience -= 1
      # print(text_input)
      try:
        if base_image:
          assert os.path.exists(base_image)
        if result_image:
          assert os.path.exists(result_image)
        if base_image: image1  = PIL.Image.open(base_image)
        if result_image: image2  = PIL.Image.open(result_image)
        if few_shot:
          examples = []
          for i in range(len(user_prompt) - 1):
            examples.append(user_prompt[i][0])
            examples.append(PIL.Image.open(user_prompt[i][1]))
          request = [text_input] + examples + [user_prompt[-1][0]] + [image1] if base_image else [] + [image2] if result_image else []
          # print(request)
        else:
          request = [text_input] + [image1] if base_image else [] + [image2] if result_image else []

        response = self.model.generate_content(request, stream=False, 
          generation_config=genai.types.GenerationConfig(
            max_output_tokens=1000,
            temperature=0)
        ).text
        response = response.strip()
        if verify_response(response):
            return response
        else:
            print(response)
            continue
      except Exception as e:
        print(e)
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)
    return ""