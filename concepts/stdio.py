import os
import asyncio
from dotenv import load_dotenv
import anthropic

async def main(): 
        
    try: 
        load_dotenv()

        # Initialize the Anthropic client
        client = anthropic.Anthropic()
        system_message = "You are a helpful assistant."
        model = os.getenv("ANTHROPIC_MODEL")

        # Initialize conversation history
        messages = []

        while True:
            user_text = input("User: ")

            # Exit condition
            if user_text.lower() in ('quit', 'exit', 'stop'):
                print('Exiting program...')
                break

            # Add user message to the conversation history
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_text
                    }
                ]
            }
            messages.append(user_message)

            # Call the LLM model
            assistant_response = await call_llm_model(
                system_message=system_message,
                messages=messages,
                model=model,
                client=client
            )
            print(f"Assistant: {assistant_response}")

            # Convert the assistant response to the expected format
            assistant_message = {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": assistant_response
                    }
                ]
            }

            # Add the assistant message to the conversation history
            messages.append(assistant_message)

    except Exception as ex:
        print(ex)


async def call_llm_model(system_message, messages, model, client):
    # Get response from Anthropic API
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=1,
        system=system_message,
        messages=messages
    )

    return message.content[0].text


# Ensure the script runs as a standalone program
if __name__ == '__main__': 
    asyncio.run(main())