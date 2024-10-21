import json
import os
import argparse

import datetime

from tqdm import tqdm
from calculate_score import update_report
from models.llava import LlavaModel

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

import random

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
  
  return system_prompt, user_prompt, image1, image2 if modalities == "image+image" else None
    

def construct_prompts_few_shot(task, subset):
  system_prompt = system_prompts['few-shot']['scratch']['image_only']
  # pick 4 numbers from 1 to 70 except for the task  
  pop = list(range(1, 71))
  if int(task['id']) in pop:
    pop.remove(int(task['id']))
  numbers = random.sample(pop, 4)
  # # for fun
  # numbers = random.sample(pop, 3)
  # numbers.append(int(task['id']))
  # # end of fun
  examples_list = []
  for number in numbers:
    example = next((task for task in subset if task['id'] == number and task['question_number'] == 1), None)
    if example: 
        examples_list.append(example)
  
  example_prompts = []
  for example in examples_list:
    example_prompt = user_prompts['few_shot']['scratch'].format(
      code=example['base_shape_code'],
      variables=example['variables']
    )
    example_prompts.append((example_prompt, example['base_shape']))
  final_query = user_prompts['scratch']['image_only'] + "\n" + user_prompt_final_piece.format(variables=task['variables'])
  example_prompts.append((final_query, task['base_shape']))
  return system_prompt, example_prompts, task['base_shape'], None


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
  elif model_name == 'llava':
    api_key = os.getenv('REPLICATE_API_TOKEN')
    model = LlavaModel(api_key=api_key)
  time = datetime.datetime.now().strftime("%d-%m_%H:%M")
  run_name = '|'.join([model_name, task_type, task_mode, modalities, 
  prompting_mode, time])

  if save_responses:
    responses_path = '.responses/' + run_name
    os.makedirs(responses_path)
    images_path = responses_path + "_images/"
    os.makedirs(images_path)
  else:
    global temp_manager
    temp_manager = TempDirManager()
    responses_path = temp_manager.create_subfolder(run_name)
    images_path = temp_manager.create_subfolder(run_name + "_images")
  
  solved_counter = 0
  pbar = tqdm(total=len(subset), desc="Processing tasks")
  run_settings = {
    "model_name": model_name,
    "task_type": task_type,
    "task_mode": task_mode,
    "modalities": modalities,
    "prompting_mode": prompting_mode,
    "time": time
  }
  update_report(run_setting=run_settings.copy(), accuracy=None, solved_counter=None)
  prompt_settings = {key: value for key, value in run_settings.items() if key not in ['time', 'model_name']}

  for task in subset:
    if prompting_mode == 'few-shot':
      system_prompt, user_prompt, image1, image2 = construct_prompts_few_shot(task, subset)
    else:
      system_prompt, user_prompt, image1, image2 = construct_prompts(
        task=task,
        **prompt_settings
      )
    task_name = str(task['id']) + '_' + str(task['question_number'])
    if model_name == 'gemini':
      response = model.get_response(system_message=system_prompt, user_prompt=user_prompt, base_image=image1, \
        result_image=image2, few_shot=prompting_mode=='few-shot')
    elif model_name=='gpt4-v':
      response = model.get_response(system_message=system_prompt, user_message=user_prompt, \
          base_image=image1, result_image=image2 , few_shot=prompting_mode=='few-shot')
    elif model_name=='llava':
      text_input = system_prompt + '\n' * 3 + user_prompt
      response = model.get_response(text_input=text_input, base_image=image1)
    try:
      assert response != None
      response_piece_of_code = preprocess_response(response)
    except Exception as e:
      print(f"Task {task_name} unsuccessful")
      print(e)
    finally:
      with open(os.path.join(responses_path, task_name + '.txt'), 'w') as f:
        f.write(response)

    code_runnable = code_to_image(response_piece_of_code, task_name, save_path=images_path)
    if code_runnable:
      solved = calculate_accuracy(task_name, source_path='autotest/source', response_path=images_path)
      if solved:
        solved_counter += 1
    
    current_accuracy = (solved_counter / (pbar.n + 1)) * 100
    pbar.set_postfix(accuracy=f"{current_accuracy:.2f}%")
    pbar.update(1)

  pbar.close()
  if not save_responses:
    temp_manager.close_temp_directory()

  update_report(run_settings, solved_counter, current_accuracy)
  print(f'Accuracy: {solved_counter * 100 / len(subset):.2f}%, Solved {solved_counter} from {len(subset)}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evaluation on different models and tasks.")
    
    parser.add_argument('--model_name', type=str, default='gemini', 
          help='The model name to use. Options are "gpt4-v", "gemini", and "llava". Default is "gemini".')
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

