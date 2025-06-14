import os
import json
from openai import AzureOpenAI 

# endpoint = os.getenv("ENDPOINT")
endpoint = "https://alakhaieastus2.openai.azure.com/"
deployment = os.getenv("DEPLOYMENT")
subscription_key = os.getenv("OPENAI_KEY")

# Print the output in readable JSON format
def chat_with_openAI(userPrompt: str, systemPrompt: str):
    print(endpoint, deployment, subscription_key)
    '''
    Function to chat with open-ai-mode gpt-4.1
    '''
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint, # type: ignore
        api_key=subscription_key,
        api_version="2025-01-01-preview",
    )

    # Prepare the chat prompt
    chat_prompt = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": systemPrompt}
            ]
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": userPrompt}
            ]
        },
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Hello! How can I help you today?"}
            ]
        }
    ]

    # Send the request to the chat model
    response = client.chat.completions.create(
        model=deployment,
        messages=chat_prompt,
        max_tokens=100,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=False
    ) # type: ignore
    
    # ✅ MODIFIED: Save full model response to output.json
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(response.model_dump(), f, ensure_ascii=False, indent=2)

    # ✅ You can still print if needed
    print(json.dumps(response.model_dump(), indent=2))
    
    messageResponse = response.choices[0].message.content
    
    return messageResponse




