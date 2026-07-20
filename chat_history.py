import os

import azure.identity
import openai
from dotenv import load_dotenv

# Setup the OpenAI client to use either Azure, OpenAI.com, or Ollama API
load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "github")

if API_HOST == "azure":
    token_provider = azure.identity.get_bearer_token_provider(
        azure.identity.DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    client = openai.OpenAI(
        base_url=f"{os.environ['AZURE_OPENAI_ENDPOINT'].rstrip('/')}/openai/v1/",
        api_key=token_provider,
    )
    MODEL_NAME = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
elif API_HOST == "ollama":
    client = openai.OpenAI(base_url=os.environ["OLLAMA_ENDPOINT"], api_key="nokeyneeded")
    MODEL_NAME = os.environ["OLLAMA_MODEL"]

elif API_HOST == "github":
    client = openai.OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=os.environ["GITHUB_TOKEN"],
    )
    MODEL_NAME = os.getenv("GITHUB_MODEL", "openai/gpt-4o")
    USE_CHAT_COMPLETIONS = True

else:
    client = openai.OpenAI(api_key=os.environ["OPENAI_KEY"])
    MODEL_NAME = os.environ["OPENAI_MODEL"]


messages = [
    {"role": "system", "content": "I am a teaching assistant helping with Python questions for Berkeley CS 61A."},
]
#Github support
#Sends whole history per question so model has some memory or context to conversation
if USE_CHAT_COMPLETIONS:
    while True:
        question = input("\nYour question: ")
        print("Sending question...")

        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5,
            store=False,
        )
        bot_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": bot_response})

        print("Answer: ")
        print(bot_response)

else:
#ANything else
    while True:
        question = input("\nYour question: ")
        print("Sending question...")

        messages.append({"role": "user", "content": question})
        response = client.responses.create(
            model=MODEL_NAME,
            input=messages,
            temperature=0.5,
            store=False,
        )
        bot_response = response.output_text
        messages.append({"role": "assistant", "content": bot_response})

        print("Answer: ")
        print(bot_response)
