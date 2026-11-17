from common import MODEL, client
from prompts import LEVEL_2_INSTRUCTIONS


previous_response_id = None

while True:
    user_input = input("You: ")

    if user_input in ("結束", "exit"):
        break

    response = client.responses.create(
        model=MODEL,
        instructions=LEVEL_2_INSTRUCTIONS,
        input=user_input,
        previous_response_id=previous_response_id
    )

    print(response.output_text)

    previous_response_id = response.id

