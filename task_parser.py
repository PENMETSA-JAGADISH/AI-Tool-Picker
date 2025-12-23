import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_subtasks(task: str) -> list:
    prompt = f"""
You are an expert AI task analyst.
Your job is to identify **if the task is atomic** (can be completed using a single AI tool) or multiple tasks.

If the task is atomic, return:
1. The exact type of AI tool needed to complete it in one step (no breakdown){task}

If the task is complex (truly requires multiple tool types){task}, return:
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

Now analyze this task:  
Task: {task}  
Output:
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        content = response.text

        # Parse response into list (assumes lines like: "1. AI tool that...")
        subtasks = []
        for line in content.strip().splitlines():
            if line.strip() and any(char.isdigit() for char in line):
                task_description = line.split('.', 1)[-1].strip()
                subtasks.append(task_description)

        return subtasks
    except Exception as e:
        print(f"[❌] Error getting subtasks: {e}")
        return []
