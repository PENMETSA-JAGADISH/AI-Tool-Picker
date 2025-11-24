def compare_and_recommend(top_tools, web_tools):
    # Combine both sources
    combined = top_tools + web_tools

    # Deduplicate by normalized name
    print(top_tools)
    print("hi")
    print(web_tools)
    seen = set()
    unique_tools = []

    for tool in combined:
        name = tool["name"].strip().lower()
        if name not in seen:
            seen.add(name)
            unique_tools.append(tool)

    # Calculate score for each tool
    def compute_score(tool):
        return (
            int(tool.get("accuracy", 0)) +
            int(tool.get("speed", 0)) +
            int(tool.get("design", 0)) +
            int(tool.get("adoption", 0)) +
            int(tool.get("reliability", 0))
        )

    # Sort tools by score descending
    ranked = sorted(unique_tools, key=compute_score, reverse=True)

    return ranked
