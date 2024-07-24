import os
import json
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.expanduser('~/shared_env/.env'))

# Setup Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def read_file(file_path):
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

def generate_questions(text, num_questions=20):
    try:
        print(f"Generating {num_questions} questions...")
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            system="You are a seasoned Journalist like Becky Quick. Generate insightful questions and answers based on the provided text.",
            messages=[
                {"role": "user", "content": f"""Analyze this text and generate {num_questions} high-quality questions and answers:

    {text}

    Focus on diverse, insightful questions covering various aspects of the text. 
    Prioritize quality over quantity. Each question-answer pair should provide valuable insights.

    Format your response as follows:

    Q1: [Your question here]
    A1: [Your detailed answer here]

    Q2: [Your next question here]
    A2: [Your detailed answer here]

    ... and so on."""}
            ]
        )
        return response.content[0].text
    except Exception as e:
        print(f"An error occurred while generating questions: {e}")
    return None

def parse_and_format_response(response_text):
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

def main():
    input_file = "cma_files/PoorCharliesAlmanack.txt"
    output_file = "PoorCharliesAlmanack_1.jsonl"

    input_text = read_file(input_file)
    if not input_text:
        print("No input text to process. Exiting.")
        return

    all_formatted_data = []
    num_calls = 50  # Number of API calls to make
    questions_per_call = 20  # Number of questions to request per call

    for i in range(num_calls):
        print(f"\nMaking API call {i + 1} of {num_calls}")
        response_text = generate_questions(input_text, questions_per_call)
        formatted_data = parse_and_format_response(response_text)
        all_formatted_data.extend(formatted_data)

    if not all_formatted_data:
        print("No formatted data to write. Exiting.")
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in all_formatted_data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        print(f"Analysis complete. {len(all_formatted_data)} new question-answer pairs saved to '{output_file}'")
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")

if __name__ == "__main__":
    main()