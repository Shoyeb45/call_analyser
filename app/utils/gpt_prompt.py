import os
import json
from openai import AzureOpenAI 
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
)
load_dotenv()
# endpoint = os.getenv("ENDPOINT")
endpoint = "https://alakhaieastus2.openai.azure.com/"
deployment = os.getenv("DEPLOYMENT")
subscription_key = os.getenv("OPENAI_KEY")

# Print the output in readable JSON format
def chat_with_openAI(userPrompt: str, systemPrompt: str):
    logging.info(f"Sending the text to gpt-4.1")
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
        max_tokens=4000,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=False
    ) # type: ignore
    
    
    messageResponse = response.choices[0].message.content
    
    return messageResponse


def check_false_claims(transcript: str, constraints: str):
    logging.info("Checking false claims...")
    constraints = constraints.split("|")
    prompt = f"""
You are an AI compliance assistant. A company has provided these factual constraints, there are several constrain, analyse each:
{str(constraints)}

Now analyze the following call transcript and find any statements that contradict these facts. 
For each contradiction, return:
- The conflicting phrase
- The matched constraint
- Why it is a violation

Transcript:
\"\"\"{transcript}\"\"\"

Match the constraint with the ouptut index.
Respond in only a json format as follows :
{{
    result: [
        {{
            \"matched_constraint\": \"the matched_constraint\",
            \"phrase\" : \"The phrase\",                   # JSON object for first constraint
            \"why_violation\": \"violation\"
        }}, {{
            \"matched_constraint\": \"the matched_constraint\",
            \"phrase\" : \"The phrase\",                   # JSON object for second constraint
            \"why_violation\": \"violation\"
        }},
        ..
        {{
            # JSON object for last constraint
        }}
    ]
}}
"""

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint, # type: ignore
        api_key=subscription_key,
        api_version="2025-01-01-preview",
    )

    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
        
    res = response.choices[0].message.content.strip()
    res = json.loads(res)
    return res
