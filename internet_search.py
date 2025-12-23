import os
import requests
import json
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SERPER_URL = "https://google.serper.dev/search"

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Helper function to search a single site (for parallel processing)
def _search_single_site(site: str, task_query: str, headers: dict):
    """Search a single site and return results"""
    query = f"{task_query} site:{site}"
    payload = {
        "q": query,
        "num": 10,
        "gl": "us",
        "hl": "en"
    }

    try:
        response = requests.post(SERPER_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        results = response.json().get("organic", [])

        site_results = []
        for item in results:
            link = item.get("link", "")
            if any(ext in link for ext in [".com", ".ai"]) and not any(excl in link for excl in ["reddit.com/r/", "/comments/", "news.ycombinator.com"]):
                site_results.append({
                    "title": item.get("title", ""),
                    "link": link,
                    "snippet": item.get("snippet", ""),
                    "source": site
                })
        return site_results
    except Exception as e:
        print(f"[❌] Error searching {site}: {e}")
        return []

# Step 1: Search Google with site-specific constraints (parallelized)
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
    
    # Parallelize site searches for better performance
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_site = {
            executor.submit(_search_single_site, site, task_query, headers): site 
            for site in sites
        }
        
        for future in as_completed(future_to_site):
            site_results = future.result()
            all_results.extend(site_results)

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

    return summarize_tools(formatted_text,task_query)

# Step 3: Ask Gemini AI to summarize the top tools
def summarize_tools(tool_text_block: str,task: str):
    prompt = f"""
You're an expert AI tool analyst. Analyze the following list of tools based on speed, performance, accuracy, and usefulness accorging to the task : {task}.
and the tool list:
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
rate the tool based on the task and it's funtionality with the task {task} if the ai tool is not highly relavent to the task then rate with zeros 0
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        content = response.text

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
