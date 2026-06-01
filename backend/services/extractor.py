"""
Extractor Module — LLM Call #1
Takes raw resume text → returns clean structured JSON.
Called ONCE per session.
"""
import json
import os
import requests
from pathlib import Path


GROQ_API_KEY = "YOUR_API_KEY"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


def extract_structured_data(raw_text: str) -> dict:
    # Trim text to avoid token limit — 3000 chars is enough for any resume
    raw_text = raw_text[:3000]

    prompt = f"""
You are a resume parser. Extract ALL information from the resume below and return ONLY valid JSON.
No explanation, no markdown, no code fences. Just raw JSON.

Extract into this exact structure:
{{
  "name": "full name",
  "email": "email",
  "phone": "phone number",
  "location": "city, country",
  "linkedin": "linkedin url or empty string",
  "github": "github url or empty string",
  "portfolio": "portfolio url or empty string",
  "summary": "professional summary or objective",
  "skills": {{
    "technical": ["skill1", "skill2"],
    "soft": ["skill1", "skill2"],
    "tools": ["tool1", "tool2"],
    "languages": ["language1"]
  }},
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "location": "city",
      "start_date": "Mon Year",
      "end_date": "Mon Year or Present",
      "bullets": ["achievement 1", "achievement 2"]
    }}
  ],
  "education": [
    {{
      "degree": "degree name",
      "institution": "university name",
      "location": "city",
      "graduation_year": "Year",
      "gpa": "GPA or empty",
      "relevant_courses": ["course1"]
    }}
  ],
  "projects": [
    {{
      "name": "project name",
      "description": "what it does",
      "tech_stack": ["tech1", "tech2"],
      "link": "url or empty",
      "bullets": ["point1", "point2"]
    }}
  ],
  "certifications": [
    {{
      "name": "cert name",
      "issuer": "issuer",
      "year": "year"
    }}
  ],
  "achievements": ["achievement1", "achievement2"]
}}

RESUME TEXT:
{raw_text}
"""

    response = _call_groq(prompt)
    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return _fallback_extraction(raw_text)


def _call_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in .env file. Get your free key at console.groq.com")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.1
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
    
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _fallback_extraction(raw_text: str) -> dict:
    import re
    email = re.findall(r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b', raw_text)
    phone = re.findall(r'\b[\+\d][\d\s\-().]{7,}\d\b', raw_text)
    return {
        "name": "Unknown",
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "location": "",
        "linkedin": "",
        "github": "",
        "portfolio": "",
        "summary": "",
        "skills": {"technical": [], "soft": [], "tools": [], "languages": []},
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "achievements": []
    }
