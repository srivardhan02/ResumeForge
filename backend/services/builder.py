"""
builder.py  –  ResumeForge
Tailors resume by INJECTING missing keywords only.
Does NOT reorder sections, rename fields, or hallucinate content.
Returns: { "resume": dict, "added_keywords": list, "ats_score": int }
"""

import json
import re
import requests

GROQ_API_KEY = "YOUR_API_KEY"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


SYSTEM_PROMPT = """You are a surgical resume editor. You make MINIMAL targeted edits to improve ATS keyword coverage.

ABSOLUTE RULES — violating any of these is a failure:
1. Do NOT reorder any sections or fields.
2. Do NOT rename any JSON keys.
3. Do NOT change dates, job titles, company names, institutions, or project names.
4. Do NOT remove any existing content.
5. Do NOT invent new jobs, projects, certifications, or skills the candidate doesn't have.
6. ONLY allowed edits:
   a) Rephrase or extend existing bullet points to include a missing keyword naturally
   b) Add missing keywords to the skills dict under the most fitting existing category
   c) Lightly reword the summary/objective sentence to weave in 1-2 missing keywords — same meaning, same length
7. If a keyword does not genuinely apply to this candidate, skip it. Never force it.
8. Return ONLY raw valid JSON — no markdown fences, no explanation, no preamble.

Output schema (strict):
{
  "resume": { ...exact same structure as input, with minimal targeted edits... },
  "added_keywords": ["keyword1", "keyword2"],
  "ats_score": <integer 0-100, honest recalculation>
}"""


def build_resume(structured: dict, job_description: str, match_result: dict) -> dict:
    """
    Inject missing keywords into existing resume content.
    Returns dict with keys: resume, added_keywords, ats_score
    """
    missing_kw  = match_result.get("high_priority_missing", [])
    all_missing = match_result.get("missing_keywords", [])
    old_score   = match_result.get("ats_score", 0)

    # Merge high-priority + regular missing, deduplicated, max 20
    targets = list(dict.fromkeys(missing_kw + all_missing))[:20]

    user_prompt = f"""Current resume JSON:
{json.dumps(structured, indent=2)}

Job description:
{job_description}

Missing keywords to inject (inject only those that genuinely apply):
{json.dumps(targets)}

Current ATS score: {old_score}%

Instructions:
- Inject applicable missing keywords naturally into existing bullets, skills, or summary.
- Do not reorder sections or change factual info.
- Return the JSON object described in the system prompt."""

    raw = _call_groq(user_prompt, max_tokens=4000)

    # Strip accidental markdown fences
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON object from messy response
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
            except json.JSONDecodeError:
                result = {}
        else:
            result = {}

    # Validate and fill defaults
    if not isinstance(result.get("resume"), dict):
        result["resume"] = structured          # fall back to original
    if not isinstance(result.get("added_keywords"), list):
        result["added_keywords"] = []
    if not isinstance(result.get("ats_score"), int):
        result["ats_score"] = old_score

    # Safety: ensure critical identity fields weren't changed
    resume = result["resume"]
    resume["name"]  = structured.get("name",  resume.get("name", ""))
    resume["email"] = structured.get("email", resume.get("email", ""))
    resume["phone"] = structured.get("phone", resume.get("phone", ""))

    return result


def _call_groq(prompt: str, max_tokens: int = 4000) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,   # Low temp = more predictable, less hallucination
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
