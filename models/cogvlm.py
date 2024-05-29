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

class CogVLMModel:
  def __init__(self, api_key, patience=1, sleep_time=1) -> None:
    self.patience = patience
    self.sleep_time = sleep_time
    self.api_key = api_key
    # self.model = genai.GenerativeModel('gemini-pro-vision')
  
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
          "yorickvp/llava-v1.6-mistral-7b:19be067b589d0c46689ffa7cc3ff321447a441986a7694c01225973c2eafc874",
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


# m = CogVLMModel(api_key="r8_bqEJg2VbuRje7gIYYImpPhqTod2rwRI2DAKj7")
# print(m.get_response("write a code in python turtle that creates a pentagon", None))