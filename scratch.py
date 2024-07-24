import os
import json
from dotenv import load_dotenv
import anthropic
from openai import OpenAI
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
# Load environment variables
load_dotenv(dotenv_path=os.path.expanduser('~/shared_env/.env'))
# Setup clients
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
client_openai = OpenAI()
client_openai.api_key = os.getenv("OPENAI_API_KEY")
mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))


# #anthropic
# message = anthropic_client.messages.create(
#     model="claude-3-5-sonnet-20240620",
#     max_tokens=1024,
#     messages=[
#         {"role": "user", "content": "Hello, Claude"}
#     ]
# )
# print(message)
# print(message.content)

model = 'gpt-4o-mini'
response = client_openai.chat.completions.create(
    model=model,
    messages=[
        {"role": "system",
         "content": "You are a seasoned Journalist like Becky Quick."
                    "Generate insightful questions and answers based on the provided text."},
        {"role": "user", "content": "how is the weather in seattle?"}
    ]
)
print(response)
tokens_used = response.usage.total_tokens
print(response.choices[0].message.content)
print(tokens_used)
