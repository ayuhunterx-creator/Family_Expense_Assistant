from common import MODEL, client
from prompts import LEVEL_1_INSTRUCTIONS

user_input = input("You: ")

response = client.responses.create(
    model=MODEL,
    instructions=LEVEL_1_INSTRUCTIONS,
    input=user_input
)

print(response.output_text)