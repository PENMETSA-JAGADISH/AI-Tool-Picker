import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_json_from_codeblock(text):
    # If the response is wrapped in a ```json ... ``` block, extract the inside
    if text.startswith("```"):
        lines = text.strip().splitlines()
        # Remove the first (```json or ```) and last (```) lines
        if len(lines) > 2:
            return "\n".join(lines[1:-1])
    return text

def get_top_tools_from_web(subtask):
    prompt = f"""
Act as an AI tools expert. Your job is to recommend the most recently popular and high-performing AI tools for the task: {subtask}

pick the top AI tools only at present
follow the latest trending tools for that task
Return the **5 most up-to-date and widely adopted tools** — including any that recently went viral
Only include tools that launched or are actively used in present times.  Include only real, working tools."
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

Note: only give the tools for that specific task only and be consistent give only the ai tools that highly relevent to the task ({subtask})
example:
task: ai tool for vibe coding
give the best ai tools for vibe coding only
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        raw_text = response.text
        cleaned_json = extract_json_from_codeblock(raw_text)
        return json.loads(cleaned_json)
    except Exception as e:
        print(f"[❌] Error getting top tools: {e}")
        return []
