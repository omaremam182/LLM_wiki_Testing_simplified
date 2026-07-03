import os
import json
from pathlib import Path
from typing import List, Dict

from langchain_core.messages import SystemMessage, HumanMessage


# -----------------------------
# Load all markdown files
# -----------------------------
def load_md_files(folder: str = "raw") -> List[Dict]:
    files = []

    for file in os.listdir(folder):
        if file.endswith(".md"):
            path = os.path.join(folder, file)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            files.append({
                "filename": file,
                "content": content
            })

    return files


# -----------------------------
# System Prompt builder
# -----------------------------
def generate_system_prompt(md_files: List[Dict]) -> str:
    context = ""

    for f in md_files:
        context += f"\n\n# {f['filename']}\n{f['content']}\n"

    return f"""
You are a helpful assistant.

Use the following markdown knowledge base to answer the user:

{context}
"""


# -----------------------------
# Save memory (conversation history)
# -----------------------------
def save_memory(path: str, messages: List[Dict]):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


# -----------------------------
# Load memory
# -----------------------------
def load_memory(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# Generate mapping.json
# -----------------------------
def generate_mapping(llm, md_files: List[Dict]) -> List[Dict]:
    mapping = []

    for f in md_files:
        prompt = f"""
Summarize this markdown file in 1-2 lines only.
Extract 3-7 keywords.

Return JSON ONLY in this format:
{{
  "title": "...",
  "summary": "...",
  "keywords": ["...", "..."]
}}

CONTENT:
{f['content']}
"""

        response = llm.invoke(prompt)

        try:
            data = json.loads(response.content)
        except:
            data = {
                "title": f["filename"],
                "summary": response.content[:200],
                "keywords": []
            }

        data["file"] = f["filename"]
        mapping.append(data)

    return mapping


# -----------------------------
# Save selected files content
# -----------------------------
def load_selected_files(selected_files: List[str], folder: str = "raw") -> str:
    context = ""

    for file in selected_files:
        path = os.path.join(folder, file)

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                context += f"\n\n# {file}\n{f.read()}"

    return context