import os
import json
import re


def clean_json(content):
    print(f"Original content (first 200 chars): {content[:200]}")

    # Remove any trailing commas before closing braces or brackets
    content = re.sub(r',\s*([\]}])', r'\1', content)

    # Remove any potential line breaks within the JSON content
    content = content.replace('\n', ' ').replace('\r', '')

    print(f"Cleaned content (first 200 chars): {content[:200]}")

    # Attempt to parse and re-serialize to ensure valid JSON
    try:
        parsed = json.loads(content)
        return json.dumps(parsed)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}")
        return None


def convert_to_jsonl(json_content):
    data = json.loads(json_content)
    if isinstance(data, dict) and 'messages' in data:
        messages = data['messages']
        jsonl_content = []
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                user_message = messages[i]
                assistant_message = messages[i + 1]
                if user_message.get('role') == 'user' and assistant_message.get('role') == 'assistant':
                    json_obj = {
                        "messages": [
                            user_message,
                            assistant_message
                        ]
                    }
                    jsonl_content.append(json.dumps(json_obj))
                else:
                    print(f"Skipping invalid message pair at index {i}")
        return '\n'.join(jsonl_content)
    return None


def process_file(file_path):
    base_name = os.path.splitext(file_path)[0]
    cleaned_file_path = f"{base_name}_cleaned.json"
    jsonl_file_path = f"{base_name}.jsonl"

    print(f"\nProcessing file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    cleaned_content = clean_json(content)
    if cleaned_content:
        with open(cleaned_file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)
        print(f"Cleaned JSON written to: {cleaned_file_path}")

        jsonl_content = convert_to_jsonl(cleaned_content)
        if jsonl_content:
            with open(jsonl_file_path, 'w', encoding='utf-8') as file:
                file.write(jsonl_content)
            print(f"JSONL content written to: {jsonl_file_path}")
        else:
            print("Failed to convert to JSONL format")
    else:
        print("Failed to clean JSON content")

        # Attempt to process the file line by line
        print("Attempting to process file line by line...")
        jsonl_content = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                try:
                    cleaned_line = clean_json(line)
                    if cleaned_line:
                        jsonl_obj = convert_to_jsonl(cleaned_line)
                        if jsonl_obj:
                            jsonl_content.append(jsonl_obj)
                except Exception as e:
                    print(f"Error processing line {line_number}: {str(e)}")

        if jsonl_content:
            with open(jsonl_file_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(jsonl_content))
            print(f"Partial JSONL content written to: {jsonl_file_path}")
        else:
            print("Failed to process any content from the file")


def process_directory(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            process_file(file_path)


if __name__ == "__main__":
    directory = "/Users/ravivayuvegula/PycharmProjects/mistral_finetune_cma/response_files"  # Replace with your directory path
    process_directory(directory)