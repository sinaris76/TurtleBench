import argparse
import os 

import pandas as pd

from utils.code_to_image import code_to_image
from utils.code_preprocess import preprocess_response
from utils.shape_similarity import calculate_accuracy

def get_settings_from_path(path):
  folder_name = path.split('/')[-1]
  parts = folder_name.split('|')
  run_setting = {
    "model_name": parts[0],
    "task_type": parts[1],
    "task_mode": parts[2],
    "modalities": parts[3],
    "prompting_mode": parts[4],
    "time": parts[5]
  }
  return run_setting

def update_report(run_setting, solved_counter, accuracy):
  assert os.path.exists('reports/report.csv')
  df_loaded = pd.read_csv('reports/report.csv')
  df_loaded.drop(columns='Unnamed: 0', inplace=True)
  filtered_row = {k: v for k, v in run_setting.items() if k in df_loaded.columns}
  mask = (df_loaded[list(run_setting.keys())] == pd.Series(filtered_row)).all(axis=1)
  row_exists = mask.any()
  if row_exists:
    df_loaded.loc[mask, 'solved'] = solved_counter
    df_loaded.loc[mask, 'accuracy'] = accuracy
    df = df_loaded.copy()
  else:
    results = run_setting
    results['solved'] = solved_counter 
    results['accuracy'] = accuracy
    df_new = pd.DataFrame(results, index=[0])
    df = pd.concat([df_loaded, df_new], ignore_index=True)
  df.to_csv('reports/report.csv')

def calculate_score(responses_path):
  settings = get_settings_from_path(responses_path)

  tasks = os.listdir(responses_path)
  solved_counter = 0
  for task in tasks:
    task_name = task.split('.')[0]
    with open(os.path.join(responses_path, task), 'r') as f:
      response = f.read()
    response_piece_of_code = preprocess_response(response)
    images_path = responses_path + '_images/'
    os.makedirs(images_path, exist_ok=True)
    code_to_image(response_piece_of_code, task_name, save_path=images_path)
    solved = calculate_accuracy(task_name, source_path='autotest/source', response_path=images_path)
    
    if solved:
      solved_counter += 1
  
  acc = solved_counter / len(tasks)
  print(f'Score for responses in {responses_path}:', acc)
  update_report(run_setting=settings, solved_counter=solved_counter, accuracy=acc)


def main():
    parser = argparse.ArgumentParser(description='Calculate score for responses')
    parser.add_argument('responses_path', type=str, help='Path to the responses directory')
    args = parser.parse_args()

    calculate_score(args.responses_path)

if __name__ == '__main__':
    main()