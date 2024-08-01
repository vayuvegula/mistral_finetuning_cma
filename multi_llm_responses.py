import os
import json
from dotenv import load_dotenv
import anthropic
from openai import OpenAI
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import wandb
import datetime
import time

# Load environment variables
load_dotenv(dotenv_path=os.path.expanduser('~/shared_env/.env'))

# Initialize Weights & Biases
wandb.init(project="qa-generator-cma")

# Setup clients
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
client_openai = OpenAI()
client_openai.api_key = os.getenv("OPENAI_API_KEY")
mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
client_openai_nvidia = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"Input file '{file_path}' read successfully. Content length: {len(content)} characters")
        return content
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file '{file_path}': {e}")
    return ""


def generate_prompt(text: str) -> str:
    return f"""Analyze this text and generate high-quality questions and answers:

{text}

Focus on diverse, insightful questions covering various aspects of the text. 
Prioritize quality over quantity. Each question-answer pair should provide valuable insights.

Format your response as follows:

Q1: [Your question here]
A1: [Your detailed answer here]

Q2: [Your next question here]
A2: [Your detailed answer here]

... and so on."""


def generate_questions(text: str, provider: str, model: str) -> tuple:
    try:
        print(f"Generating questions using {provider} {model}...")
        prompt = generate_prompt(text)

        if provider == "anthropic":
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=4096,
                system="You are a seasoned Journalist like Becky Quick."
                       "Generate insightful questions and answers based on the provided text.",
                messages=[{"role": "user", "content": prompt}]
            )
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            response_text = "\n\n".join([block.text for block in response.content])
            return response_text, tokens_used

        elif provider == "openai":
            response = client_openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system",
                     "content": "You are a seasoned Journalist like Becky Quick."
                                "Generate insightful questions and answers based on the provided text."},
                    {"role": "user", "content": prompt}
                ]
            )
            tokens_used = response.usage.total_tokens
            return response.choices[0].message.content, tokens_used

        elif provider == "openai_nvidia":
            response = client_openai_nvidia.chat.completions.create(
                model="meta/llama-3.1-405b-instruct",
                messages=[
                    {"role": "system",
                     "content": "Follow the rules strictly and apply them to the prompt"
                                "the content is in JSON format, convert all list elements"
                                "to a JSONL format where each line {'messages': [{'role': 'user', 'content': 'Example text'}, {'role': 'assistant', 'content': 'Example text'}]}"},
                    {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        elif provider == "mistral":
            messages = [
                ChatMessage(role="system",
                            content="You are a seasoned Journalist like Becky Quick."
                                    "Generate insightful questions and answers based on the provided text."),
                ChatMessage(role="user", content=prompt)
            ]
            response = mistral_client.chat(model=model, messages=messages)
            tokens_used = 0  # No known method for token usage in Mistral, so we'll set it to 0
            return response.choices[0].message.content, tokens_used

        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except Exception as e:
        print(f"An error occurred while generating questions: {e}")
    return None, 0


def parse_and_format_response(response_text: str) -> list:
    formatted_data = []
    if response_text is None:
        return formatted_data

    pairs = response_text.split('\n\n')
    for pair in pairs:
        parts = pair.split('\n', 1)
        if len(parts) == 2:
            question = parts[0].strip().lstrip('Q1234567890:').strip()
            answer = parts[1].strip().lstrip('A1234567890:').strip()
            formatted_data.append({
                "messages": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            })
    print(f"Parsed {len(formatted_data)} question-answer pairs")
    return formatted_data


def generate_output_filename(base_name: str, provider: str, model: str, suffix: str = "") -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{provider}_{model}_{suffix}_{timestamp}.jsonl"


def log_to_wandb(data: dict):
    wandb.log(data)


def manage_processed_files(file_path: str, action: str = 'check') -> bool:
    tracking_file = 'processed_files.json'
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


EXCLUDED_FILES = [
    # Add more files to exclude as needed
]


def is_file_excluded(file_path: str) -> bool:
    return os.path.basename(file_path) in EXCLUDED_FILES


def process_file(file_path: str, provider: str, model: str):
    # Check if file is in the exclusion list
    if is_file_excluded(file_path):
        print(f"File {file_path} is in the exclusion list. Skipping.")
        return

    # Check if file has been processed before
    if manage_processed_files(file_path, 'check'):
        print(f"File {file_path} has already been processed. Skipping.")
        return

    input_text = read_file(file_path)
    if not input_text:
        print("No input text to process. Exiting.")
        return

    start_time = time.time()
    response_text, tokens_used = generate_questions(input_text, provider, model)
    end_time = time.time()

    formatted_data = parse_and_format_response(response_text)

    log_to_wandb({
        "file": file_path,
        "questions_generated": len(formatted_data),
        "sample_question": formatted_data[0]["messages"][0]["content"] if formatted_data else "No question generated",
        "sample_answer": formatted_data[0]["messages"][1]["content"] if formatted_data else "No answer generated",
        "response_time": end_time - start_time,
        "tokens_used": tokens_used
    })

    if not formatted_data:
        print("No formatted data to write. Exiting.")
        return

    output_file = generate_output_filename("output", provider, model, os.path.basename(file_path))
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in formatted_data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        print(f"Analysis complete. {len(formatted_data)} new question-answer pairs saved to '{output_file}'")

        log_to_wandb({
            "file": file_path,
            "total_questions_generated": len(formatted_data),
            "total_tokens_used": tokens_used,
            "output_file": output_file
        })

        # Mark file as processed
        manage_processed_files(file_path, 'update')
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")


def add_file_to_exclusion_list(file_name: str):
    global EXCLUDED_FILES
    if file_name not in EXCLUDED_FILES:
        EXCLUDED_FILES.append(file_name)
        print(f"Added {file_name} to exclusion list.")
    else:
        print(f"{file_name} is already in the exclusion list.")


def main(directory: str, provider: str = "anthropic", model: str = "claude-3-sonnet-20240229") -> None:
    for file_name in os.listdir(directory):
        if file_name.endswith(".txt"):
            file_path = os.path.join(directory, file_name)
            process_file(file_path, provider, model)


if __name__ == "__main__":
    main(
        directory="testing",
        provider="openai_nvidia",  # or "openai", "mistral", or "anthropic"
        model="meta/llama-3.1-405b-instruct"  # or "gpt-3.5-turbo" for OpenAI, "mistral-large-latest" for Mistral, or "claude-3-sonnet-20240229"
    )