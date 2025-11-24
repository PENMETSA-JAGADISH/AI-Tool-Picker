import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SERPER_URL = "https://google.serper.dev/search"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Step 1: Search Google with site-specific constraints
def search_ai_tools(task_query: str):
    sites = [
        "producthunt.com",
        "aiupdates.ai",
        "thereisanaiforthat.com",
        "reddit.com"
    ]

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    all_results = []
    print("\nSearching in Web....")
    for site in sites:
        query = f"{task_query} site:{site}"
        payload = {
            "q": query,
            "num": 10,
            "gl": "us",
            "hl": "en"
        }

        try:
            response = requests.post(SERPER_URL, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("organic", [])

            for item in results:
                link = item.get("link", "")
                if any(ext in link for ext in [".com", ".ai"]) and not any(excl in link for excl in ["reddit.com/r/", "/comments/", "news.ycombinator.com"]):
                    all_results.append({
                        "title": item.get("title", ""),
                        "link": link,
                        "snippet": item.get("snippet", ""),
                        "source": site
                    })

        except Exception as e:
            print(f"[❌] Error: {e}")
            continue

    # Keep only top 10 valid results
    valid_tools = all_results[:10]

    if not valid_tools:
        print("[⚠️] No valid tools found.")
        return []

    # Step 2: Format for summarization
    formatted_text = ""
    for i, tool in enumerate(valid_tools, 1):
        formatted_text += (
            f"{i}. Title: {tool['title']}\n"
            f"URL: {tool['link']}\n"
            f"Summary: {tool['snippet']}\n\n"
        )

    return summarize_tools(formatted_text)

# Step 3: Ask OpenRouter AI to summarize the top tools
def summarize_tools(tool_text_block: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You're an expert AI tool analyst. Analyze the following list of tools based on speed, performance, accuracy, and usefulness.

{tool_text_block}

For each tool, return this JSON format:
[
  {{
    "name": "Tool Name",
    "url": "https://..." url should be the original url of the name of the AI tool only,
    "accuracy": 1-4 score,
    "speed": 1-4 score,
    "design": 1-4 score,
    "adoption": 1-4 score,
    "reliability": 1-4 score,
    "reason": "Brief summary why it's popular now"
  }},
  ...
]
name should be the tool name only no other extra words
url should be the url which is the main address of the tool only no extra worls or sub pages , example goole -> https://google.com
Return only a clean JSON array. No markdown, no commentary.
"""

    payload = {
        "model": "tngtech/deepseek-r1t2-chimera:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return parse_json_response(content)

    except Exception as e:
        print(f"[❌] AI Summarization Failed: {e}")
        return []

# Clean response JSON if wrapped in code block
def parse_json_response(text):
    if text.startswith("```"):
        lines = text.strip().splitlines()
        return json.loads("\n".join(lines[1:-1]))
    return json.loads(text)