import json
import os
import tempfile
import argparse

import datetime

from tqdm import tqdm

from models.gemini import GeminiModel
from models.gpt import GPTModel
from prompts import system_prompts, user_prompts, user_prompt_final_piece
from utils.shape_similarity import calculate_accuracy
from utils.code_to_image import code_to_image
from utils.run_option_error import InconsistentKeyError

from utils.temp_directory import TempDirManager
from utils.watermark import watermark_and_save
from utils.code_preprocess import preprocess_response

from dotenv import load_dotenv

def construct_prompts(task, task_type, prompting_mode, modalities, task_mode):
  assert task_type=='scratch' or task_type=='tweak'
  try:
    if task_type == 'scratch':
      system_prompt = system_prompts[prompting_mode]['scratch'][modalities]
    elif task_type == 'tweak':
      system_prompt = system_prompts[prompting_mode]['tweak'][task_mode][modalities]
  except KeyError as e:
    raise InconsistentKeyError

  user_prompt = None
  if task_type == 'scratch':
    user_prompt = user_prompts['scratch'][modalities]
  elif task_type == 'tweak':
    user_prompt = user_prompts['tweak'][task_mode][modalities]
  
  user_prompt = user_prompt.format(
    description=task['description'],
    code=task['base_shape_code'],
    query=task['query'],
    variables=task['variables']
  )
  user_prompt += "\n" + user_prompt_final_piece.format(variables=task['variables'])
  image1 = task['base_shape']
  image2 = task['result_shape']
  if task_mode=='code_edit' and modalities=='image+image':
    watermarekd_path = temp_manager.create_subfolder('watermarked')
    image1 = watermark_and_save(task['base_shape'], watermarekd_path, '1')
    image2 = watermark_and_save(task['result_shape'], watermarekd_path, '2')
  
  return system_prompt, user_prompt, image1, image2
    
  

def eval(model_name='gpt4-v', task_type='scratch', task_mode='code_generation', modalities='image_only', 
prompting_mode='cot', code_framework='turtle', save_responses=False):
  
  tasks_config_path = 'dataset.jsonl'
  config = []
  with open(tasks_config_path, 'r') as file:
    for line in file:
        json_object = json.loads(line)
        config.append(json_object)
  if task_type == 'scratch' and 'text' in modalities:
    subset = []
    for conf in config:
      if conf['question_number'] == 1 and conf['description'] != None:
        subset += [conf]
  elif task_type == 'scratch' and not 'text' in modalities:
    subset = []
    for conf in config:
      if conf['question_number'] == 1:
        subset += [conf]
  elif task_type == 'tweak':
    subset = []
    for conf in config:
      if conf['question_number'] != 1:
        subset += [conf]
  
  load_dotenv()
  if model_name == 'gpt4-v':
    api_key = os.getenv('OPENAI_API_KEY')
    model = GPTModel(api_key=api_key)  
  elif model_name == 'gemini':
    api_key = os.getenv('GOOGLE_API_KEY')
    model = GeminiModel(api_key=api_key)
  
  global temp_manager
  temp_manager = TempDirManager()
  if save_responses:
    responses_path = '.responses/' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '_' + model_name
    os.makedirs(responses_path)
    images_path = responses_path + "_Images"
    os.makedirs(images_path)
  else:
    responses_path_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '_' + model_name
    responses_path = temp_manager.create_subfolder(responses_path_name)
    images_path = temp_manager.create_subfolder(responses_path_name + "_Images")
  
  solved_counter = 0
  pbar = tqdm(total=len(subset), desc="Processing tasks")

  for task in subset:
    system_prompt, user_prompt, image1, image2 = construct_prompts(
      task=task,
      task_type=task_type,
      task_mode=task_mode,
      modalities=modalities,
      prompting_mode=prompting_mode
    )
    task_name = str(task['id']) + '_' + str(task['question_number'])
    if model_name == 'gemini':
      text_input = system_prompt + '\n' * 3 + user_prompt
      response = model.get_response(text_input=text_input, base_image=image1, result_image=image2)
    elif model_name=='gpt4-v':
      response = model.get_response(system_message=system_prompt, user_message=user_prompt, base_image=image1, result_image=image2)
    try:
      assert response != None
      response_piece_of_code = preprocess_response(response)
    except Exception as e:
      print(f"Task {task_name} unsuccessful")
      print(e)
    finally:
      with open(responses_path + '/' + task_name + '.txt', 'w') as f:
        f.write(response)

    code_to_image(response_piece_of_code, task_name, save_path=images_path)
    
    solved = calculate_accuracy(task_name, source_path='autotest/source', response_path=images_path)
    if solved:
      solved_counter += 1
    
    current_accuracy = (solved_counter / (pbar.n + 1)) * 100
    pbar.set_postfix(accuracy=f"{current_accuracy:.2f}%")
    pbar.update(1)  

  pbar.close()
  temp_manager.close_temp_directory()

  print(f'Accuracy: {solved_counter * 100 / len(subset):.2f}%, Solved {solved_counter} from {len(subset)}')

# eval(model_name='gemini', task_type='tweak', task_mode='code_generation', modalities='image+text', save_responses=True)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evaluation on different models and tasks.")
    
    parser.add_argument('--model_name', type=str, default='gemini', 
                        help='The model name to use. Options are "gpt4-v" and "gemini". Default is "gemini".')
    parser.add_argument('--task_type', type=str, default='scratch', 
                        help='Type of task to perform. Options are "scratch" or "tweak". Default is "scratch".')
    parser.add_argument('--task_mode', type=str, default='code_generation', 
                        help='Mode of the task. Options are "code_generation" and "code_edit". Default is "code_generation".')
    parser.add_argument('--modalities', type=str, default='image_only', 
                        help='Modalities to use. Options are "image_only", "text_only", "image+text", and "image+image". Default is "image_only".')
    parser.add_argument('--prompting_mode', type=str, default='cot', 
                        help='Prompting mode to use. Options are "cot" and "basic". Default is "cot".')
    parser.add_argument('--code_framework', type=str, default='turtle', 
                        help='Framework for code generation. Default is "turtle".')
    parser.add_argument('--save_responses', action='store_true', 
                        help='Save the responses to files. Does not save by default.')

    args = parser.parse_args()
    
    eval(model_name=args.model_name, task_type=args.task_type, task_mode=args.task_mode, 
         modalities=args.modalities, prompting_mode=args.prompting_mode, code_framework=args.code_framework, 
         save_responses=args.save_responses)