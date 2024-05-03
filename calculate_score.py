import os 

from utils.code_to_image import code_to_image
from utils.code_preprocess import preprocess_response
from utils.shape_similarity import calculate_accuracy

def calculate_score(responses_path):
  tasks = os.listdir(responses_path)
  for task in tasks:
    task_name = task.split('.')[0]
    with open(responses_path + '/' + task, 'r') as f:
      response = f.read()
    response_piece_of_code = preprocess_response(response)
    images_path = responses_path + '_images/'
    os.makedirs(images_path, exist_ok=True)
    code_to_image(response_piece_of_code, task_name, save_path=images_path)
    solved = calculate_accuracy(task_name, source_path='autotest/source', response_path=images_path)
    solved_counter = 0
    if solved:
      solved_counter += 1
  
  acc = solved_counter / len(tasks)
  print(acc)
calculate_score('.responses/gemini_scratch_code_generation_image_only_cot_02/05_19:05')