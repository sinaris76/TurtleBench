from utils.code_analysis import *
import os
import subprocess

from utils.sandbox import execute_combined_code

def code_to_image(piece_of_code, task_name, save_path):
  try:
    clean_code = insert_pensize_and_hideturtle(piece_of_code)
  except Exception as e:
    print(e, task_name)
    clean_code = ""
  try:
    svn = find_screen_variable_name(clean_code)
  except:
    print("error on code:", f'{task_name}.txt')
  code = execute_combined_code(clean_code, screen_variable_name=svn, task_name=task_name, save_path=save_path)
  file_path = f'file_path_{task_name}.py'
  with open(file_path, 'w') as file:
    file.write(code)
  completed_process = subprocess.run(['python', file_path])
  if completed_process.returncode == 0:
    os.remove(file_path)
  else:
    print("Process failed, return code:", completed_process.returncode)
