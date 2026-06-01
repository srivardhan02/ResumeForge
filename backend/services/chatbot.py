"""
Chatbot Module
Handles resume correction via conversation.
Uses sliding window of last 6 messages — prevents token bloat and API overuse.
"""
import json
import os
import requests
from services.latex_generator import generate_latex

GROQ_API_KEY = "YOUR_API_KEY"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


SYSTEM_PROMPT = """You are ResumeForge AI, an expert resume editor and career coach.
You have the candidate's current tailored resume in JSON format.

Your job:
- Make specific edits the user requests (shorten summary, add keywords, rewrite bullets, etc.)
- Explain what you changed and why
- Keep all factual info accurate — never fabricate experience
- If the user asks to "update" or "change" something, return the FULL updated JSON
- If the user just asks a question (no edit needed), answer it conversationally

When making edits, ALWAYS end your response with the updated JSON in this exact format:
---UPDATED_RESUME_JSON---
{the full updated resume JSON here}
---END_JSON---

If no edit is needed (just answering a question), do NOT include the JSON block.
"""


def chat_with_resume(
    user_message: str,
    current_resume: dict,
    chat_history: list,
    structured: dict
) -> tuple[str, dict | None, str | None]:
    """
    Process a chat message for resume corrections.
    
    Returns:
        - response text (str)
        - updated_resume (dict or None)
        - updated_latex (str or None)
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set.")

    # Build messages array with sliding window
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + f"\n\nCURRENT RESUME JSON:\n{json.dumps(current_resume, indent=2)}"
        }
    ]

    # Add conversation history (sliding window — last 6 messages)
    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current message
    messages.append({"role": "user", "content": user_message})

    # Call API
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.4
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
    response.raise_for_status()
    full_response = response.json()["choices"][0]["message"]["content"]

    # Parse response — check if resume was updated
    updated_resume = None
    updated_latex = None
    display_response = full_response

    if "---UPDATED_RESUME_JSON---" in full_response:
        try:
            parts = full_response.split("---UPDATED_RESUME_JSON---")
            display_response = parts[0].strip()

            json_part = parts[1].split("---END_JSON---")[0].strip()
            updated_resume = json.loads(json_part)
            updated_latex = generate_latex(updated_resume)
        except (json.JSONDecodeError, IndexError):
            # If parsing fails, keep original resume
            updated_resume = None
            updated_latex = None
            display_response = full_response

    return display_response, updated_resume, updated_latex
