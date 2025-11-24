import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

def get_subtasks(task: str) -> list:
    prompt = f"""
You are an expert AI task analyst.
Your job is to identify **if the task is atomic** (can be completed using a single AI tool).

If the task is atomic, return:
1. The exact type of AI tool needed to complete it in one step (no breakdown)

If the task is complex (truly requires multiple tool types), return:
1. Subtasks strictly as AI tool functions — only list AI tool categories (not user steps or logic)

Only return the **minimal list of AI tools** required to solve the task, one per line.
Do not include tools like "AI tool that writes text" unless it's core to the task.

Examples:

Task: I want to generate a video using a prompt  
Output:  
1. AI tool that converts prompt to video 

Task : Best AI Chatbot
output:
1. Best AI chatbot to Chat

Task: I need to transcribe a YouTube video and translate it to French  
Output:  
1. AI tool that transcribes YouTube videos  
2. AI tool that translates text to French  

Task: I want an AI tool to generate a pitch deck for my startup idea  
Output:  
1. AI tool that generates pitch decks from startup ideas  

Task: I want to generate product images from description  
Output:  
1. AI tool that generates product images from text  

i need a json file of this format

    "choices": 
            "message": 
                "content": "some text"

Now analyze this task:  
Task: {task}  
Output:
"""

    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    data = response.json()
    print(data)
    content = data["choices"][0]["message"]["content"]

    # Parse response into list (assumes lines like: "1. AI tool that...")
    subtasks = []
    for line in content.strip().splitlines():
        if line.strip() and any(char.isdigit() for char in line):
            task_description = line.split('.', 1)[-1].strip()
            subtasks.append(task_description)

    return subtasks