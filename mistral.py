from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.expanduser('~/shared_env/.env'))

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"
prompt = " A cavernous factory in northeastern Tennessee, by the Virginia border, "
"is one of the last in the country that makes a vitally important medicine."
"Each day the USAntibiotics plant churns out a million doses of the crucial antibiotic amoxicillin that promise to cure Americans of everything from earaches to pneumonia—and ease a pressing shortage for children.)"
"But the plant’s prospects are dim. It can’t charge enough to cover overhead, because competitors sell their wares at bargain prices. USAntibiotics isn’t close to breaking even."
"“It’s not for lack of trying,” said Rick Jackson, a health-staffing businessman who rescued the factory from near bankruptcy two years ago and has poured more than $38 million into purchasing and refurbishing it."
"The generic drug business has become a hostile environment for American companies. Prices for the often critical medicines have dropped so low that it has become difficult for U.S. manufacturers to compete with companies overseas. "
"Rick Jackson, founder and chief executive officer of Jackson Healthcare.One after another, generic-drug makers have gone bankrupt or moved their operations overseas or cut the number of products they offer. The number of facilities making generic drugs in"
" their final form in the U.S. has dropped by roughly 20% since 2018,"
"to 243, according to federal data.Drug shortages have become common. Today, 300 medicines are in short supply, ""according to the American Society of Health-System Pharmacists. Regularly now, hospitals and patients must scramble "
"to find doses of the drugs they need if there is one hiccup in a pinched supply chain or a quality problem shuts "
"down a manufacturing line." "Doctors, patients and policymakers, including former President Donald Trump and President Biden, have decried the shortages and called for fixes."
" Among the prescriptions: reinvigorating American manufacturing. But little has been done."
client = MistralClient(api_key=api_key)

chat_response = client.chat(
    model=model,
    messages=[
        {"role": "system",
         "content": "You are Charlie Munger the renowed investor, using your wisdom and all your teachings"
                    "Generate insightful observations based on the provided text."},
        {"role": "user", "content": prompt}]
)
print(chat_response.choices[0].message.content)
