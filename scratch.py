# import os
# import json
# from dotenv import load_dotenv
# import anthropic
# from openai import OpenAI
# from mistralai.client import MistralClient
# from mistralai.models.chat_completion import ChatMessage
# # Load environment variables
# load_dotenv(dotenv_path=os.path.expanduser('~/shared_env/.env'))
# # Setup clients
# anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# client_openai = OpenAI()
# client_openai.api_key = os.getenv("OPENAI_API_KEY")
# mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
#
#
# # #anthropic
# # message = anthropic_client.messages.create(
# #     model="claude-3-5-sonnet-20240620",
# #     max_tokens=1024,
# #     messages=[
# #         {"role": "user", "content": "Hello, Claude"}
# #     ]
# # )
# # print(message)
# # print(message.content)
#
# model = 'gpt-4o-mini'
# response = client_openai.chat.completions.create(
#     model=model,
#     messages=[
#         {"role": "system",
#          "content": "You are a seasoned Journalist like Becky Quick."
#                     "Generate insightful questions and answers based on the provided text."},
#         {"role": "user", "content": "how is the weather in seattle?"}
#     ]
# )
# print(response)
# tokens_used = response.usage.total_tokens
# print(response.choices[0].message.content)
# print(tokens_used)
import torch
import torch.nn as nn
from collections import OrderedDict

# Define the model
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Sets the parameters of the model
def set_weights(net, parameters):
    params_dict = zip(net.state_dict().keys(), parameters)
    state_dict = OrderedDict(
        {k: torch.tensor(v) for k, v in params_dict}
    )
    net.load_state_dict(state_dict, strict=True)

# Retrieves the parameters from the model
def get_weights(net):
    ndarrays = [
        val.cpu().numpy() for _, val in net.state_dict().items()
    ]
    return ndarrays

# Instantiate the model
net = SimpleNet()

# Get initial weights
initial_weights = get_weights(net)
print("Initial Weights:")
for i, w in enumerate(initial_weights):
    print(f"Weight {i}: {w.shape}")

# Create dummy new weights (random values with the same shape as initial weights)
new_weights = [torch.rand_like(torch.tensor(w)).numpy() for w in initial_weights]

print("\nNew Weights:")
for i, w in enumerate(new_weights):
    print(f"New Weight {i}: {w.shape}")

# Set the new weights to the model
set_weights(net, new_weights)

# Verify the weights have been updated
updated_weights = get_weights(net)
print("\nUpdated Weights:")
for i, w in enumerate(updated_weights):
    print(f"Updated Weight {i}: {w.shape}")