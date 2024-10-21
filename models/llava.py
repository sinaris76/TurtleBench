import os 
import time

import replicate

def verify_response(response):
    if isinstance(response, str):
        response = response.strip() 
    if response == "" or response == None:
        return False
    if "Response Error" in response:
        # print("Response Error")
        return False
    return True

class LlavaModel:
  def __init__(self, api_key, patience=1, sleep_time=1) -> None:
    self.patience = patience
    self.sleep_time = sleep_time
    self.api_key = api_key
  
  def get_response(self, text_input, base_image):
    patience = self.patience
    while patience > 0:
      patience -= 1
      # print(text_input)
      try:
        if base_image:
          assert os.path.exists(base_image)
        if base_image: image1  = open(base_image, 'rb')
        input_ = {
          "prompt": text_input,
          "image": image1
        }
        if base_image:
          input_["image"] = image1
        output = replicate.run(
          "yorickvp/llava-13b:b5f6212d032508382d61ff00469ddda3e32fd8a0e75dc39d8a4191bb742157fb",
          input=input_
        )
        response = "".join(output)
        if verify_response(response):
            return response
        else:
            print(response)
      except Exception as e:
        print(e)
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)
    return ""

