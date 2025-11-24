from task_parser import get_subtasks
from top_tools import get_top_tools_from_web
from internet_search import search_ai_tools
from tool_ranker import compare_and_recommend
from storage.db import save_tool_data

if __name__ == "__main__":
    task = input("Enter your task:\n>")
    while not task:
        task = input("Enter your task:\n> ")
    print("\nUnderstanding your goal...")
    subtask = get_subtasks(task)
    print(f"\nSubtask: {subtask}")
    for i in subtask:
        print("\n🤖 searching for top tools...")
        top_tools = get_top_tools_from_web(subtask)

        print("\n🌐 Searching top directories...")
        web_tools = search_ai_tools(subtask)

        print("\n📊 top tools and Web results...")
        final_tools = compare_and_recommend(top_tools, web_tools)

        print("\n✅ Top Recommended Tools:")
        for i, tool in enumerate(final_tools, 1):
            print(f"\n{i}. {tool['name']}\n   URL: {tool['url']}\n   Reason: {tool['reason']}")

        save_tool_data(subtask, final_tools)