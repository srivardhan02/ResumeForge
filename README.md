# ⬡ ResumeForge

AI-powered resume tailoring web app. Upload your resume + a job description → get a tailored resume in PDF and LaTeX format, with an AI chatbot to refine it further.

---

## What it does

1. **Upload** your resume (PDF / DOCX / TXT) + paste a job description
2. **Analysis** — ATS keyword score and gap analysis using Python keyword matching
3. **Generate** — LLaMA 3 70B (via Groq) tailors your resume for the specific role
4. **Edit** — Chat with AI to fix anything in real time
5. **Download** — PDF (compiled from LaTeX) or raw `.tex` file

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React 18 |
| Backend | FastAPI (Python) |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| ATS Scoring | Python keyword matching (string-based) |
| LLM | Groq API — LLaMA 3.3 70B |
| LaTeX → PDF | pdflatex (texlive) |
| Chat Memory | Sliding window (last 6 messages) |

---

## How the ATS Score Works

1. Groq (LLaMA 3 70B) parses your raw resume into structured JSON — LLM Call #1
2. The job description is tokenized into keywords using pure Python (no LLM)
3. Each keyword is checked against the structured resume text — simple string matching
4. `ATS Score = (matched keywords / total JD keywords) × 100`
5. High-priority missing keywords (tech terms like Python, Docker, etc.) are flagged separately

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free Groq API key: https://console.groq.com
- pdflatex: `sudo apt-get install texlive-latex-base texlive-fonts-recommended`

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

python main.py
# Runs at http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
# Runs at http://localhost:3000
```

---

## Project Structure

```
Resumeforge/
├── backend/
│   ├── main.py                  # FastAPI app, all routes
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py
│   └── services/
│       ├── parser.py            # PDF/DOCX/TXT extraction
│       ├── extractor.py         # LLM call #1: resume → structured JSON
│       ├── matcher.py           # ATS keyword scoring (no LLM)
│       ├── builder.py           # LLM call #2: tailored resume
│       ├── latex_generator.py   # LaTeX template + PDF compile
│       └── chatbot.py           # Chat with sliding window memory
└── frontend/
    └── src/
        ├── App.jsx
        └── pages/
            ├── Upload.jsx       # Step 1: upload + job description
            ├── Results.jsx      # Step 2: ATS score + analysis
            └── Editor.jsx       # Step 3: preview + chat + download
```
---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload` | Upload resume + JD → ATS analysis |
| POST | `/api/generate` | Generate tailored resume |
| POST | `/api/download/pdf` | Compile and download PDF |
| GET | `/api/download/latex/{id}` | Download .tex file |
| POST | `/api/chat` | Chat to edit resume |
| GET | `/api/session/{id}` | Get session state |

---

## API Usage (Groq Free Tier)

- 14,400 requests/day, 30 req/min — plenty for personal/portfolio use
- Each resume generation = 2 LLM calls (extract + build)
- Chat uses sliding window (last 6 messages) to keep token usage low
- Cost for personal use = $0

---

## Deploy

**Backend (Render):**
- Add `GROQ_API_KEY` as an environment variable in the Render dashboard
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Frontend (Vercel):**
- Set `REACT_APP_API_URL` to your Render backend URL
- Run `vercel deploy`
