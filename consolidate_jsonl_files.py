import os
import json
import time
import datetime


def manage_processed_files(file_path: str = None, action: str = 'check'):
    tracking_file = 'processed_jsonl_files.json'
    if not os.path.exists(tracking_file):
        with open(tracking_file, 'w') as f:
            json.dump({}, f)

    with open(tracking_file, 'r+') as f:
        processed_files = json.load(f)

        if action == 'check':
            return file_path in processed_files
        elif action == 'update':
            processed_files[file_path] = time.time()
            f.seek(0)
            json.dump(processed_files, f)
            f.truncate()
            return True
        elif action == 'reset':
            processed_files.clear()
            f.seek(0)
            json.dump(processed_files, f)
            f.truncate()
            return True


def consolidate_jsonl_files(directory: str, output_base_name: str, reset: bool = False):
    if reset:
        manage_processed_files(action='reset')
        print("Reset the tracking of processed files.")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_base_name}_{timestamp}.jsonl"

    with open(output_file, 'a', encoding='utf-8') as outfile:
        for file_name in os.listdir(directory):
            if file_name.endswith(".jsonl"):
                file_path = os.path.join(directory, file_name)

                # Skip already processed files
                if manage_processed_files(file_path, 'check'):
                    print(f"File {file_path} has already been processed. Skipping.")
                    continue

                with open(file_path, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        outfile.write(
                            line.rstrip() + '\n')  # Strip any existing trailing newlines and add a single newline

                # Mark file as processed
                manage_processed_files(file_path, 'update')
                print(f"Consolidated file {file_path}")

    print(f"All files consolidated into {output_file}")


if __name__ == "__main__":
    consolidate_jsonl_files(
        directory="response_files",  # Replace with your directory path
        output_base_name="consolidated_jsonl",
        reset=True  # Set to True to reset the tracking and process all files again
    )