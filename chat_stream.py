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

if USE_CHAT_COMPLETIONS:
    # IF API Host is github
    completion_stream = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "You are a helpful assistant that makes lots of cat references and uses emojis."},
        {"role": "user", "content": "please write a haiku about a hungry cat that wants tuna"},
    ],
    temperature=0.7,
    stream=True,)
    print(f"Response from {API_HOST}: \n")

    for chunk in completion_stream:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta.content

        if delta:
            print(delta, end="", flush=True)

    print()

else:
    # Anything else
    completion_stream = client.responses.create(
    model=MODEL_NAME,
    temperature=0.7,
    input=[
        {"role": "system", "content": "You are a helpful assistant that makes lots of cat references and uses emojis."},
        {"role": "user", "content": "What's the weather in SF today?"},
    ],
    store=False,)

    print(f"Response from {API_HOST}: \n")
    for event in completion_stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "response.completed":
            print()

    

