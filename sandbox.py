import json
import os

# Function to read and extract code from the JSON file
def get_code_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data['python_code']  # Replace 'python_code' with the actual key
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to combine and execute the entire code
def execute_combined_code(code, model, image_id, question_number, screen_variable_name):
    # Your Python code before the JSON code
    pre_json_code = """import subprocess\nimport os""" 
    if screen_variable_name:
      post_json_code = open('post_code_with_screen_name.txt', 'r').read().\
      format(model = model, id = image_id, question_number=question_number, screen_variable_name=screen_variable_name)
    else:
      post_json_code = open('post_code.txt', 'r').read().format(model = model, id = image_id, question_number=question_number)
    
    # Combine the code segments
    combined_code = pre_json_code + code + post_json_code if code else None
    return(combined_code)
