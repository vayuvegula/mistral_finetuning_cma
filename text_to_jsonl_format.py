import os
import json

def convert_and_rename(file_path):
    new_file_path = file_path.replace('.jsonl.txt', '.jsonl')
    print(f"Converting {file_path} to {new_file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            print(f"Read {len(lines)} lines from {file_path}")

        jsonl_content = []
        for line in lines:
            line = line.strip()
            if line:
                try:
                    json_obj = json.loads(line)
                    jsonl_content.append(json_obj)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line in file {file_path}: {line}")

        with open(new_file_path, 'w', encoding='utf-8') as file:
            for json_obj in jsonl_content:
                file.write(json.dumps(json_obj) + '\n')
        print(f"Written {len(jsonl_content)} lines to {new_file_path}")

        os.remove(file_path)  # Remove the old .txt file
        print(f"Removed old file {file_path}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def convert_files_in_directory(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith(".jsonl.txt"):
            file_path = os.path.join(directory, file_name)
            print(f"Processing file {file_path}")
            convert_and_rename(file_path)

if __name__ == "__main__":
    directory = "/Users/ravivayuvegula/PycharmProjects/mistral_finetune_cma/response_files"  # Replace with your directory path
    convert_files_in_directory(directory)