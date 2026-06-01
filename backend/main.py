from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import json
import os
from services.parser import parse_resume
from services.extractor import extract_structured_data
from services.matcher import keyword_match
from services.builder import build_resume
from services.latex_generator import generate_latex, compile_to_pdf
from services.chatbot import chat_with_resume
from models.schemas import ChatRequest, ChatResponse, ResumeSession
from services.pdf_generator import generate_pdf
import traceback

SESSION_FILE = "sessions.json"
app = FastAPI(title="ResumeForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, ResumeSession] = {}


@app.get("/")
def root():
    return {"status": "ResumeForge API running"}


@app.post("/api/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """Step 1: Upload resume + JD → session_id + structured data + ATS score"""
    try:
        content  = await resume.read()
        filename = resume.filename.lower()

        raw_text   = parse_resume(content, filename)
        structured = extract_structured_data(raw_text)
        match_result = keyword_match(structured, job_description)

        import uuid
        session_id = str(uuid.uuid4())
        sessions[session_id] = ResumeSession(
            session_id=session_id,
            raw_text=raw_text,
            structured=structured,
            job_description=job_description,
            match_result=match_result,
            tailored_resume=None,
            chat_history=[]
        )

        return {
            "session_id":   session_id,
            "structured":   structured,
            "match_result": match_result,
            "status":       "success"
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_resume(session_id: str = Form(...)):
    """
    Step 2: Inject missing keywords → tailored resume + keyword report + new ATS score.
    build_resume() returns: { resume, added_keywords, ats_score }
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    try:
        # ── Core call ──────────────────────────────────────────────────────
        result = build_resume(
            structured=session.structured,
            job_description=session.job_description,
            match_result=session.match_result,
        )

        tailored      = result["resume"]           # updated resume dict
        added_kw      = result["added_keywords"]   # list of injected keywords
        new_ats_score = result["ats_score"]         # new score after injection
        old_ats_score = session.match_result.get("ats_score", 0)

        # Generate LaTeX (kept for /api/download/latex)
        latex_code = generate_latex(tailored)

        # Persist to session
        session.tailored_resume = tailored
        session.latex_code      = latex_code
        sessions[session_id]    = session.dict()

        with open(SESSION_FILE, "w") as f:
            json.dump(sessions, f, indent=2)

        return {
            "tailored_resume":   tailored,
            "latex_code":        latex_code,
            "added_keywords":    added_kw,          # ← NEW: what was injected
            "new_ats_score":     new_ats_score,      # ← NEW: score after tailoring
            "original_ats_score": old_ats_score,     # ← NEW: score before tailoring
            "score_improvement": new_ats_score - old_ats_score,
            "status": "success"
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/download/pdf")
async def download_pdf(session_id: str = Form(...)):
    """Step 3: Generate PDF from tailored resume dict"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = sessions[session_id]
    session = ResumeSession(**session_data) if isinstance(session_data, dict) else session_data

    if not session.tailored_resume:
        raise HTTPException(status_code=400, detail="Resume not generated yet")

    try:
        os.makedirs("generated", exist_ok=True)
        pdf_path = f"generated/{session_id}.pdf"
        generate_pdf(session.tailored_resume, pdf_path)
        return FileResponse(pdf_path, media_type="application/pdf", filename="tailored_resume.pdf")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/latex/{session_id}")
async def download_latex(session_id: str):
    """Download raw LaTeX as .tex file"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    if not session.latex_code:
        raise HTTPException(status_code=400, detail="Resume not generated yet")

    tex_path = f"/tmp/{session_id}.tex"
    with open(tex_path, "w") as f:
        f.write(session.latex_code)
    return FileResponse(tex_path, media_type="text/plain", filename="resume.tex")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chatbot: correct/modify resume via conversation (sliding window of 6 messages)"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = sessions[request.session_id]
    session = ResumeSession(**session_data) if isinstance(session_data, dict) else session_data

    try:
        response, updated_resume, updated_latex = chat_with_resume(
            user_message=request.message,
            current_resume=session.tailored_resume,
            chat_history=session.chat_history[-6:],
            structured=session.structured
        )

        session.chat_history.append({"role": "user",      "content": request.message})
        session.chat_history.append({"role": "assistant", "content": response})

        if updated_resume:
            session.tailored_resume = updated_resume
            session.latex_code      = updated_latex

        return ChatResponse(
            response=response,
            updated_resume=updated_resume,
            updated_latex=updated_latex
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
