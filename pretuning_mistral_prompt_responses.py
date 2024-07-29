##
# from mistralai.client import MistralClient
# from mistralai.models.chat_completion import ChatMessage
# import os
# from dotenv import load_dotenv
# import wandb
# import json
# from datetime import datetime
#
# # Load environment variables
# load_dotenv(dotenv_path=os.path.expanduser('~/shared_env/.env'))
#
# api_key = os.environ["MISTRAL_API_KEY"]
# model = "mistral-large-latest"
#
# # Initialize wandb with project and entity names
# wandb.init(project="mistral_experiments_pretuning")
#
# # Define the function to read text files
# def read_prompts_from_files(directory):
#     prompts = {}
#     print(f"Reading files from directory: {directory}")
#     for filename in os.listdir(directory):
#         print(f"Found file: {filename}")
#         if filename.endswith(".txt"):
#             filepath = os.path.join(directory, filename)
#             with open(filepath, 'r') as file:
#                 content = file.read()
#                 prompts[filename] = content
#                 print(f"Read content from {filename}")
#     return prompts
#
# # Define the function to get responses from Mistral
# def get_mistral_responses(prompts):
#     client = MistralClient(api_key=api_key)
#     responses = {}
#     for filename, prompt in prompts.items():
#         print(f"Processing file: {filename}")
#         chat_response = client.chat(
#             model=model,
#             messages=[
#                 {"role": "system",
#                  "content": "You are Charlie Munger, the renowned investor, using your wisdom and all your teachings"
#                             "Generate insightful observations based on the provided text."},
#                 {"role": "user", "content": prompt}
#             ]
#         )
#         response_text = chat_response.choices[0].message.content
#         responses[prompt] = {
#             "response": response_text,
#             "model": model,
#             "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         }
#         # Log the query and response to wandb
#         wandb.log({
#             "filename": filename,
#             "prompt": prompt,
#             "response": response_text,
#             "model": model,
#             "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         })
#     return responses
#
# # Main execution
# prompts_directory = "pretuning_prompts"
# prompts = read_prompts_from_files(prompts_directory)
# responses = get_mistral_responses(prompts)
#
# # Save responses dictionary to a JSON file
# output_file = f"responses_{model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
# with open(output_file, 'w') as f:
#     json.dump(responses, f, indent=4)
#
# # Print responses (optional)
# for prompt, response in responses.items():
#     print(f"Prompt: {prompt}\nResponse: {response['response']}\n")
#
# # Finish the wandb run
# wandb.finish()

import os
import json
from dotenv import load_dotenv
import wandb
import weave
from datetime import datetime
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Load environment variables
load_dotenv(dotenv_path=os.path.expanduser('~/shared_env/.env'))

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

# Initialize wandb
wandb.init(project="mistral_experiments_pretuning")

# Initialize weave
weave.init("mistral_experiments_pretuning")

# Define the function to read text files
def read_prompts_from_files(directory):
    prompts = {}
    print(f"Reading files from directory: {directory}")
    for filename in os.listdir(directory):
        print(f"Found file: {filename}")
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                content = file.read()
                prompts[filename] = content
                print(f"Read content from {filename}")
    return prompts

# Define the Weave operation to get responses from Mistral
@weave.op()
def get_response_from_mistral(prompt: str) -> dict:
    client = MistralClient(api_key=api_key)
    chat_response = client.chat(
        model=model,
        messages=[
            {"role": "system",
             "content": "You are Charlie Munger, the renowned investor, using your wisdom and all your teachings"
                        "Generate insightful observations based on the provided text."},
            {"role": "user", "content": prompt}
        ]
    )
    response_text = chat_response.choices[0].message.content
    return {
        "prompt": prompt,
        "response": response_text,
        "model": model,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Main execution
prompts_directory = "pretuning_prompts"
prompts = read_prompts_from_files(prompts_directory)
responses = {}

for filename, prompt in prompts.items():
    print(f"Processing file: {filename}")
    response_data = get_response_from_mistral(prompt)
    responses[filename] = response_data
    # Log the query and response to wandb
    wandb.log({
        "filename": filename,
        "prompt": response_data["prompt"],
        "response": response_data["response"],
        "model": response_data["model"],
        "date": response_data["date"]
    })

# Save responses dictionary to a JSON file
output_file = f"responses_{model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(responses, f, indent=4)

# Print responses (optional)
for filename, response in responses.items():
    print(f"Filename: {filename}\nPrompt: {response['prompt']}\nResponse: {response['response']}\n")

# Finish the wandb run
wandb.finish()