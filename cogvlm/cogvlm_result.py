import json 

def extract_chat_answers_updated(file_path, answer_key):
    answers = []
    with open(file_path, 'r') as file:
        for line in file:
            json_object = json.loads(line)
            # Extract the answer using the provided key
            if answer_key in json_object:
                answers.append(json_object[answer_key])
    return answers

# Key for extracting answers from the first file
answer_key_v1 = 'cogvlm_chat_with_figure_answer'

# Extract answers from both files
answers_v1 = extract_chat_answers_updated('test_answered_v1.jsonl', answer_key_v1)
answers_v2 = extract_chat_answers_updated('test_answered_v1.jsonl', answer_key_v1)

for i, ans in enumerate(answers_v2):
  with open(f'cogvlm_v2_res/{i}', "w+") as f:
    f.write(ans)
