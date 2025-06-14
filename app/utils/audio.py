import ffmpeg
import tiktoken
from app.utils.gpt_prompt import chat_with_openAI
from elevenlabs.types import SpeechToTextWordResponseModel
import json
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
)

def tokenize_content(text: str, max_input_tokens=4096, max_output_tokens=512) -> str:
    """
    Tokenizes and truncates Hindi input if needed, then sends to GPT-4.1 for summarization.
    """
    # Initialize GPT-4 tokenizer
    encoding = tiktoken.encoding_for_model("gpt-4")
    
    # Tokenize the text
    input_tokens = encoding.encode(text)

    # Truncate input tokens if they exceed the max input limit
    if len(input_tokens) > max_input_tokens:
        print(f"Input too long ({len(input_tokens)} tokens), truncating to {max_input_tokens} tokens.")
        input_tokens = input_tokens[:max_input_tokens]

    # Decode tokens back to text (if truncated)
    truncated_text = encoding.decode(input_tokens)
    
    # Return the model's reply
    return truncated_text


        
def summarise_text(text):
    logging.info("Summarising the text")
    systemPrompt = """
You are a call analysis assistant. You are also an expert in analyzing human emotions from Hindi or Hinglish text. Analyze the same call transcript and give a single summary of the emotional distribution as probabilities (not sentence-wise). Given a transcript in Hindi or Hinglish, analyze and respond in the following JSON format:

{
  "summary": "A concise summary of the call (3-4 lines).",
  "sentiment": {
    "overall_sentiment": "neutral" | "positive" | "negative",
    "distributed_sentiment": {
      "joy": float,
      "sadness": float,
      "anger": float,
      "frustration": float,
      "confusion": float,
      "empathy": float,
      "surprise": float,
      "sarcasm": float,
      "laughter": float,
      "fear": float,
      "disgust": float,
      "neutral": float
    }
  },
  "abusive_words": [list of abusive words found, if any]
}

Instructions:
- "summary": Write a concise summary of the call in bulleted point, give the markdown text as string as a value in this key.
- "sentiment": 
    - "overall_sentiment": One of "neutral", "positive", or "negative" for the entire call.
    - "distributed_sentiment": Assign a probability (float between 0 and 1) to each emotion listed above. The sum must be 1.
- "abusive_words": List any abusive words found in the transcript. If none, return an empty list.

Respond ONLY with a valid JSON object as shown above.
"""
    text = tokenize_content(text=text)
    userPrompt = f"""
Here is the audio transcription in Hindi/Hinglish:
\"\"\"
{text}
\"\"\"
"""
    
    res = chat_with_openAI(userPrompt, systemPrompt)
    logging.info(f"Response from chatgpt : {res}")
    # Convert this into the object fron json string
    res = json.loads(res)
    
    return res["summary"], res["sentiment"], res["abusive_words"]
        


def convert_to_wav(input_path, output_path):
    logging.info("Converting to wav....")
    ffmpeg.input(input_path).output(output_path, ar=16000, ac=1).run(overwrite_output=True)

def analyze_emotions(text):
    systemPrompt = f"""
You are an expert in analyzing human emotions from Hindi or Hinglish text. Analyze the following call transcript and give a single summary of the emotional distribution as probabilities (not sentence-wise).

Use ONLY the following fixed emotions: joy, sadness, anger, frustration, confusion, empathy, surprise, sarcasm, laughter, fear, disgust, neutral.

Output a valid JSON object with each emotion as a key, and a float between 0 and 1 as value. The sum of all values must equal 1 (normalized distribution).

Example format:
{{
  "joy": 0.2,
  "sadness": 0.3,
  "anger": 0.1,
  ...
}}
"""
    userPrompt = f"""Here is the call recording: 
\"{text}\""""
    


    result = chat_with_openAI(systemPrompt, userPrompt)
    

    return result

def seconds_to_min_sec(seconds):
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}:{secs:02d}"

from collections import defaultdict

def to_list(response: defaultdict):
    ans = []
    for key in response.keys():
        ans.append({
            "word": key,
            "timestamps": response[key]
        })
    
    return ans

def abusive_words_analyse(abuse_words : list, words: list[SpeechToTextWordResponseModel]):
    response = defaultdict(list)
    logging.info("Analysing abusive words")
    for word in words:
        # print(word.text)
        for abuse_word in abuse_words:
            if abuse_word in word.text:
                response[abuse_word].append(seconds_to_min_sec(word.start))
    
    response = to_list(response)
    return response