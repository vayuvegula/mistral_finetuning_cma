import json
import os

def text_to_jsonl(input_dir, output_dir):
    """
    Convert text files to JSONL format and save them in the output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.txt'):
            with open(os.path.join(input_dir, file_name), 'r') as text_file:
                lines = text_file.readlines()

            jsonl_content = []
            for line in lines:
                try:
                    json_obj = json.loads(line.strip())
                    jsonl_content.append(json.dumps(json_obj))
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file {file_name}, line: {line.strip()}")

            jsonl_file_name = file_name.replace('.txt', '.jsonl')
            with open(os.path.join(output_dir, jsonl_file_name), 'w') as jsonl_file:
                jsonl_file.write('\n'.join(jsonl_content))

def consolidate_jsonl(input_dir, consolidated_file):
    """
    Consolidate all JSONL files in the input directory into a single JSONL file.
    """
    try:
        with open(consolidated_file, 'w') as output_file:
            for file_name in os.listdir(input_dir):
                if file_name.endswith('.jsonl'):
                    with open(os.path.join(input_dir, file_name), 'r') as jsonl_file:
                        for line in jsonl_file:
                            output_file.write(line)
                            output_file.write('\n')
    except OSError as e:
        print(f"Error: {e}")

# Define directories
input_dir = 'response_files'  # Replace with the directory containing your text files
output_dir = 'consolidated_jsonl'  # Replace with the directory to save JSONL files
consolidated_file = 'consolidated_jsonl/consolidated.jsonl'  # Replace with the path to save the consolidated file

# Convert text files to JSONL format
text_to_jsonl(input_dir, output_dir)

# Consolidate JSONL files into a single file
consolidate_jsonl(output_dir, consolidated_file)