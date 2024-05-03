from utils.sandbox import execute_combined_code
from utils.code_analysis import find_screen_variable_name, insert_pensize_and_hideturtle
import subprocess
import os

def generate_image(variables, code, task_name):
  whole_code = """import turtle\nfrom math import *\nt = turtle.Turtle()\n""" + variables + "\n" + code
  clean_code = insert_pensize_and_hideturtle(whole_code)
  code = execute_combined_code(clean_code, None, 'autotest/source', task_name)
  file_path = f'file_path_source_{task_name}.py'
  with open(file_path, 'w') as file:
    file.write(code)
  completed_process = subprocess.run(['python', file_path])
  if completed_process.returncode == 0:
    os.remove(file_path)
  else:
    print("Process failed, return code:", completed_process.returncode)
