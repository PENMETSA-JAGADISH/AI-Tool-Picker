from task_parser import get_subtasks
from top_tools import get_top_tools_from_web
from internet_search import search_ai_tools
from tool_ranker import compare_and_recommend

from concurrent.futures import ThreadPoolExecutor

if __name__ == "__main__":
    task = input("Enter your task:\n>")
    while not task:
        task = input("Enter your task:\n> ")
    print("\nUnderstanding your goal...")
    subtask = get_subtasks(task)
    print(f"\nSubtask: {subtask}")
    
    for i in subtask:
        print(f"\n🔍 Processing subtask: {i}")
        
        # Parallelize top_tools and web_search for better performance
        print("\n🤖 Searching for top tools and web directories in parallel...")
        with ThreadPoolExecutor(max_workers=2) as executor:
            top_tools_future = executor.submit(get_top_tools_from_web, i)
            web_tools_future = executor.submit(search_ai_tools, i)
            
            top_tools = top_tools_future.result()
            web_tools = web_tools_future.result()

        print("\n📊 Ranking top tools and Web results...")
        final_tools = compare_and_recommend(top_tools, web_tools)

        print("\n✅ Top Recommended Tools:")
        c=0
        for idx, tool in enumerate(final_tools, 1):
            if c==5:
                break
            c+=1

            print(f"\n{idx}. {tool['name']}\n   URL: {tool['url']}\n   Reason: {tool['reason']}")
