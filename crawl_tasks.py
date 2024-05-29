import os
import re
import json
from utils.generate_source_images import generate_image
from utils.contours import find_contour, preprocess_image

tasks = os.listdir('Tasks')
numeric_tasks = [item for item in tasks if item.isdigit()]
tasks = sorted(numeric_tasks, key=lambda x: int(x))
print(tasks)


def extract_number_from_filename(filename):
    match = re.search(r'q(\d+)_*', filename)
    if match:
        return int(match.group(1))  # Convert the matched string to an integer
    else:
        return None



def create_jsonl_from_folders(folder_path, generate_source_images):
    # JSONL file to store the output
    jsonl_file_path = 'dataset.jsonl'

    with open(jsonl_file_path, 'w') as jsonl_file:
        # Iterating through each numbered directory
        tasks = []
        for folder_name in os.listdir(folder_path):
          if not folder_name.isnumeric():
            continue
          tasks += [folder_name]
        numeric_tasks = [item for item in tasks if item.isdigit()]
        tasks = sorted(numeric_tasks, key=lambda x: int(x))
        for task in tasks:
            # if 27 < int(task) or  int(task) < 26:
            #   continue
            # Paths for the QA text and image directories
            qa_text_path = os.path.join(folder_path, task, 'QA', 'text')
            image_path = os.path.join(folder_path, task, 'image', f'{task}.png')
            code_files_path = os.path.join(folder_path, task, 'QA', 'code')
            # Reading all text files in the QA text directory
            for text_file in os.listdir(qa_text_path):
                question_number = extract_number_from_filename(text_file)
                if text_file.startswith('.'): 
                  continue
                text_file_path = os.path.join(qa_text_path, text_file)
                variable_file_path = os.path.join(folder_path, task, 'variables.txt')
                description_file_path = os.path.join(folder_path, task, 'description.txt')
                code_text_path = os.path.join(code_files_path, f'q{question_number}_code.txt')
                with open(code_text_path, 'r') as f:
                    code = f.read()
                if not os.path.exists(variable_file_path):
                  variables_text = None
                else:
                  with open(variable_file_path, 'r') as f:
                    variables_text = f.read()
                description = None
                if os.path.exists(description_file_path):
                  with open(description_file_path, 'r') as f:
                    description = f.read()
                # Reading the contents of the text file
                with open(text_file_path, 'r') as file:
                    text_content = file.read().strip()
                result_shape_path  = os.path.join(folder_path, task, 'result_image', f'q{question_number}_image.png')
                if generate_source_images and variables_text:
                    try:
                      generate_image(variables_text, code, f'{int(task)}_{question_number}')
                    except Exception as e: 
                      print(e)

                # Creating the JSON object
                json_object = {
                    "id": int(task),
                    "question_number": question_number,
                    "query": text_content,
                    "base_shape": f'autotest/source/{task}_1.jpg',
                    "result_shape": result_shape_path,
                    "variables": variables_text,
                    "base_shape_code": code,
                    "source_contours": find_contour(preprocess_image(f'autotest/source/{task}_1.jpg'))[1],
                    "description": description 
                }
                # Writing the JSON object to the JSONL file
                jsonl_file.write(json.dumps(json_object) + '\n')


# Calling the function and passing the path of the extracted folder
create_jsonl_from_folders('Tasks', generate_source_images = True)
