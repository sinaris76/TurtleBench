import os
import re
import json

tasks =  os.listdir('Tasks')
numeric_tasks = [item for item in tasks if item.isdigit()]
tasks = sorted(numeric_tasks, key=lambda x: int(x))
print(tasks)


def extract_number_from_filename(filename):
    match = re.search(r'q(\d+)_*', filename)
    if match:
        return int(match.group(1))  # Convert the matched string to an integer
    else:
        return None



def create_jsonl_from_folders(folder_path):
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
        print(tasks)
        for task in tasks:

            # Paths for the QA text and image directories
            qa_text_path = os.path.join(folder_path, task, 'QA', 'text')
            image_path = os.path.join(folder_path, task, 'image', f'{task}.png')

            # Reading all text files in the QA text directory
            for text_file in os.listdir(qa_text_path):
                if text_file.startswith('.'): 
                  continue
                text_file_path = os.path.join(qa_text_path, text_file)
                
                # Reading the contents of the text file
                with open(text_file_path, 'r') as file:
                    print(text_file_path)
                    text_content = file.read().strip()

                # Creating the JSON object
                json_object = {
                    "id": task,
                    "question_number": extract_number_from_filename(text_file),
                    "query": text_content,
                    "base_shape": image_path
                }

                # Writing the JSON object to the JSONL file
                jsonl_file.write(json.dumps(json_object) + '\n')

# Calling the function and passing the path of the extracted folder
create_jsonl_from_folders('Tasks')
