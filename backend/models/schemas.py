from pydantic import BaseModel
from typing import Optional, Any


class ResumeSession(BaseModel):
    session_id: str
    raw_text: str
    structured: dict
    job_description: str
    match_result: dict
    tailored_resume: Optional[dict] = None
    latex_code: Optional[str] = None
    chat_history: list = []


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    updated_resume: Optional[dict] = None
    updated_latex: Optional[str] = None
