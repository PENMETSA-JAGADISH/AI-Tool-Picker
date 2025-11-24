
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

def extract_json_from_codeblock(text):
    # If the response is wrapped in a ```json ... ``` block, extract the inside
    if text.startswith("```") and text.endswith("```"):
        lines = text.strip().splitlines()
        # Remove the first (```json) and last (```) lines
        return "\n".join(lines[1:-1])
    return text

def get_top_tools_from_web(subtask):
    prompt = f"""
Act as an AI tools expert. Your job is to recommend the most recently popular and high-performing AI tools for the task: {subtask}

pick the top AI tools only at present
Search across trending sources like Product Hunt, Futurepedia, Reddit, Twitter, and AI news.
follow the latest trending tools for that task
Return the **10 most up-to-date and widely adopted tools** — including any that recently went viral like Lovable, Bolt, Framer AI, etc.
Only include tools that launched or are actively used in present times.  Include only real, working tools.”
also don't give tools from same website just give the tool name not model names

For each tool, return this JSON format:
[
  {{
    "name": "Tool Name",
    "url": "https://...",
    "accuracy": 1-5 score,
    "speed": 1-5 score,
    "design": 1-5 score,
    "adoption": 1-5 score,
    "reliability": 1-5 score,
    "recent_launch": true/false,
    "reason": "Brief summary why it's popular now"
  }},
  ...
]
name should be the tool name only no other extra words
url should be the url which is the main address of the tool only no extra words , example goole -> https://google.com 
Output as a clean JSON list only — no markdown or explanation.
"""


    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    try:
        result = response.json()
        raw_text = result["choices"][0]["message"]["content"]
        cleaned_json = extract_json_from_codeblock(raw_text)
        return json.loads(cleaned_json)
    except Exception:
        return []
