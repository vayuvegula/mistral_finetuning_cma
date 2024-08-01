import jsonlines
import json
import os
import re


def clean_json_string(s):
    # Remove "messages": [ if present at the start
    s = re.sub(r'^"messages":\s*\[', '', s).strip()

    # Replace incorrect double quotes with single quotes
    s = s.replace('"s', "'s").replace('."', ".'")

    # Ensure proper JSON formatting by replacing remaining single quotes with double quotes
    s = s.replace("'", '"')

    # Fix "role": "assistant": pattern
    s = re.sub(r'"assistant"\s*:', '"assistant", "content":', s)

    # Remove any trailing commas
    s = re.sub(r',\s*}$', '}', s)

    return s


def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, \
            jsonlines.open(output_path, mode='w') as writer:
        content = infile.read()

        # Extract the main JSON array
        match = re.search(r'\[(.+)\]', content, re.DOTALL)
        if match:
            json_array = match.group(1)

            # Split the array into individual JSON objects
            json_objects = re.findall(r'{.+?}(?=\s*,\s*{|\s*$)', json_array, re.DOTALL)

            for obj in json_objects:
                cleaned_obj = clean_json_string(obj)
                try:
                    parsed_obj = json.loads(cleaned_obj)
                    writer.write(parsed_obj)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse entry: {cleaned_obj[:50]}... Error: {e}")


def main():
    input_directory = 'testing'
    output_directory = 'testing/output'

    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith('.txt') or filename.endswith('.json'):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}.jsonl")

            print(f"Processing file: {input_path}")
            process_file(input_path, output_path)
            print(f"Finished processing: {input_path}")


if __name__ == "__main__":
    main()