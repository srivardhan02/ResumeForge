import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";

export default function Editor({ sessionId, resumeData, onResumeUpdate, onBack }) {
  const [tab, setTab] = useState("preview");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I'm your resume editor. Your tailored resume is ready. Ask me to make any changes — shorten the summary, add keywords, rewrite experience bullets, change the tone, anything. What would you like to improve?",
    },
  ]);
  const [input, setInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
  }, [input]);

  async function handleSend() {
    if (!input.trim() || chatLoading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setChatLoading(true);

    try {
      const res = await axios.post("/api/chat", {
        session_id: sessionId,
        message: userMsg,
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.response },
      ]);
      if (res.data.updated_resume) {
        onResumeUpdate({
          ...resumeData,
          tailored_resume: res.data.updated_resume,
          latex_code: res.data.updated_latex,
        });
        setMessages((prev) => [
          ...prev,
          { role: "system", content: "✦ Resume updated successfully" },
        ]);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Chat failed");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  async function downloadPDF() {
    try {
      const formData = new FormData();
      formData.append("session_id", sessionId);
      const res = await axios.post("/api/download/pdf", formData, { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url; a.download = "tailored_resume.pdf"; a.click();
      URL.revokeObjectURL(url);
      toast.success("PDF downloaded!");
    } catch (err) {
      toast.error("PDF download failed.");
    }
  }

  function downloadLatex() {
    const blob = new Blob([resumeData.latex_code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "resume.tex"; a.click();
    URL.revokeObjectURL(url);
    toast.success("LaTeX downloaded!");
  }

  const resume        = resumeData.tailored_resume;
  const addedKeywords = resumeData.added_keywords     || [];
  const newScore      = resumeData.new_ats_score;
  const originalScore = resumeData.original_ats_score;
  const improvement   = resumeData.score_improvement  ?? (newScore - originalScore);
  const hasReport     = addedKeywords.length > 0 || newScore != null;

  const quickPrompts = [
    "Shorten the summary",
    "Add more keywords",
    "Stronger bullets",
    "Improve ATS score",
    "Fix grammar & tone",
    "Add action verbs",
  ];

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center gap-3 mb-4">
        <button className="btn btn-ghost btn-sm" onClick={onBack}>← Back</button>
        <div>
          <h1 className="page-title" style={{ fontSize: 26, marginBottom: 0 }}>Resume Editor</h1>
          <p className="page-subtitle" style={{ marginBottom: 0, fontSize: 14 }}>
            Review your tailored resume and refine it with AI
          </p>
        </div>
      </div>

      {/* Keyword injection report */}
      {hasReport && (
        <div style={{
          background: "linear-gradient(135deg, rgba(99,102,241,0.07), rgba(165,180,252,0.04))",
          border: "1px solid rgba(99,102,241,0.2)",
          borderRadius: "var(--radius)",
          padding: "16px 22px",
          marginBottom: 20,
          display: "flex",
          gap: 28,
          flexWrap: "wrap",
          alignItems: "flex-start",
        }}>
          {/* Score comparison */}
          <div style={{ flexShrink: 0 }}>
            <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.1em", color: "var(--text3)", marginBottom: 10, textTransform: "uppercase", fontFamily: "var(--font-mono)" }}>
              ATS Score
            </p>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 24, fontWeight: 800, color: "var(--text2)", lineHeight: 1, fontFamily: "var(--font-head)" }}>{originalScore}</div>
                <div style={{ fontSize: 10, color: "var(--text3)", marginTop: 2, fontFamily: "var(--font-mono)" }}>Before</div>
              </div>
              <div style={{ fontSize: 16, color: "var(--text3)", margin: "0 2px" }}>→</div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 24, fontWeight: 800, lineHeight: 1, fontFamily: "var(--font-head)", color: newScore >= 70 ? "var(--green)" : newScore >= 45 ? "var(--yellow)" : "var(--red)" }}>
                  {newScore}
                </div>
                <div style={{ fontSize: 10, color: "var(--text3)", marginTop: 2, fontFamily: "var(--font-mono)" }}>After</div>
              </div>
              {improvement > 0 && (
                <div style={{ background: "var(--green-bg)", border: "1px solid rgba(52,211,153,0.25)", borderRadius: 8, padding: "4px 10px", fontSize: 13, fontWeight: 700, color: "var(--green)", marginLeft: 4 }}>
                  +{improvement}
                </div>
              )}
            </div>
          </div>

          <div style={{ width: 1, background: "var(--border)", alignSelf: "stretch" }} />

          {/* Added keywords */}
          <div style={{ flex: 1, minWidth: 220 }}>
            <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.1em", color: "var(--text3)", marginBottom: 10, textTransform: "uppercase", fontFamily: "var(--font-mono)" }}>
              {addedKeywords.length} Keyword{addedKeywords.length !== 1 ? "s" : ""} Injected
            </p>
            {addedKeywords.length > 0 ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {addedKeywords.map((kw) => (
                  <span key={kw} style={{ background: "rgba(99,102,241,0.12)", border: "1px solid rgba(99,102,241,0.25)", borderRadius: 6, padding: "3px 10px", fontSize: 12, fontWeight: 600, color: "var(--accent3)", display: "flex", alignItems: "center", gap: 5 }}>
                    <span style={{ color: "var(--green)", fontSize: 8 }}>✦</span>{kw}
                  </span>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: 13, color: "var(--text3)" }}>Your resume already covered the key terms well.</p>
            )}
          </div>
        </div>
      )}

      {/* Main 55/45 layout */}
      <div className="editor-layout">

        {/* ── Resume Preview Panel ── */}
        <div className="resume-preview">
          <div className="resume-tabs">
            <button className={`resume-tab ${tab === "preview" ? "active" : ""}`} onClick={() => setTab("preview")}>
              Preview
            </button>
            <button className={`resume-tab ${tab === "latex" ? "active" : ""}`} onClick={() => setTab("latex")}>
              LaTeX Source
            </button>
          </div>

          <div className="resume-content">
            {tab === "preview" ? (
              <ResumePreview resume={resume} addedKeywords={addedKeywords} />
            ) : (
              <pre className="latex-code">{resumeData.latex_code}</pre>
            )}
          </div>

          <div className="download-actions">
            <button className="btn btn-primary btn-sm" onClick={downloadPDF}>⬇ Download PDF</button>
            <button className="btn btn-secondary btn-sm" onClick={downloadLatex}>⬇ Download .tex</button>
          </div>
        </div>

        {/* ── Chat Panel ── */}
        <div className="chat-panel">

          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-dot" />
            <span style={{ fontWeight: 700, fontSize: 14, fontFamily: "var(--font-head)", letterSpacing: "-0.2px" }}>
              AI Resume Editor
            </span>
            <span className="badge badge-purple" style={{ marginLeft: "auto", fontSize: 10 }}>
              Context-aware
            </span>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-msg ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {chatLoading && (
              <div className="chat-msg assistant" style={{ opacity: 0.65, display: "flex", alignItems: "center", gap: 10 }}>
                <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2, flexShrink: 0 }} />
                <span>Editing your resume...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick prompts */}
          <div className="chat-quick-prompts">
            <p className="chat-quick-label">Quick edits</p>
            <div className="chat-quick-row">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: 11, padding: "5px 10px", borderRadius: 6 }}
                  onClick={() => setInput(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="chat-input-row">
            <textarea
              ref={textareaRef}
              className="chat-input"
              placeholder="Ask me to edit anything… (Enter to send, Shift+Enter for newline)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button
              className="chat-send-btn"
              onClick={handleSend}
              disabled={chatLoading || !input.trim()}
              title="Send (Enter)"
            >
              ↑
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

/* ── Resume Preview with keyword highlighting ── */
function ResumePreview({ resume, addedKeywords = [] }) {
  if (!resume) return <p className="text-muted">No resume generated yet.</p>;

  function highlight(text) {
    if (!text || addedKeywords.length === 0) return text;
    const escaped = addedKeywords.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const pattern = new RegExp(`(${escaped.join("|")})`, "gi");
    const parts = text.split(pattern);
    return parts.map((part, i) =>
      pattern.test(part) ? (
        <mark key={i} style={{ background: "rgba(99,102,241,0.2)", color: "var(--accent3)", borderRadius: 3, padding: "0 2px", fontWeight: 600 }}>
          {part}
        </mark>
      ) : part
    );
  }

  return (
    <div style={{ fontSize: 14 }}>
      {/* Name + contact */}
      <div style={{ marginBottom: 22, paddingBottom: 18, borderBottom: "1px solid var(--border)" }}>
        <h2 style={{ fontFamily: "var(--font-head)", fontSize: 22, fontWeight: 800, letterSpacing: "-0.3px" }}>
          {resume.name}
        </h2>
        <p className="text-muted text-sm" style={{ marginTop: 5 }}>
          {[resume.email, resume.phone, resume.location].filter(Boolean).join(" · ")}
        </p>
        {(resume.linkedin || resume.github) && (
          <p className="text-muted text-sm" style={{ marginTop: 2 }}>
            {[resume.linkedin, resume.github, resume.portfolio].filter(Boolean).join(" · ")}
          </p>
        )}
      </div>

      {resume.summary && (
        <div className="structured-section">
          <h3>Summary</h3>
          <p className="text-muted" style={{ fontSize: 13, lineHeight: 1.65 }}>{highlight(resume.summary)}</p>
        </div>
      )}

      {resume.skills && (
        <div className="structured-section">
          <h3>Skills</h3>
          {resume.skills.technical?.length > 0 && (
            <p className="text-sm" style={{ marginBottom: 6 }}>
              <strong style={{ color: "var(--text)" }}>Technical: </strong>
              <span className="text-muted">{highlight(resume.skills.technical.join(", "))}</span>
            </p>
          )}
          {resume.skills.tools?.length > 0 && (
            <p className="text-sm" style={{ marginBottom: 6 }}>
              <strong style={{ color: "var(--text)" }}>Tools: </strong>
              <span className="text-muted">{highlight(resume.skills.tools.join(", "))}</span>
            </p>
          )}
          {resume.skills.soft?.length > 0 && (
            <p className="text-sm">
              <strong style={{ color: "var(--text)" }}>Soft: </strong>
              <span className="text-muted">{resume.skills.soft.join(", ")}</span>
            </p>
          )}
        </div>
      )}

      {resume.experience?.length > 0 && (
        <div className="structured-section">
          <h3>Experience</h3>
          {resume.experience.map((exp, i) => (
            <div key={i} className="exp-item">
              <div className="flex justify-between items-center">
                <span className="exp-title">{exp.title}</span>
                <span style={{ fontSize: 11, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{exp.start_date} – {exp.end_date}</span>
              </div>
              <p className="exp-meta">{exp.company} · {exp.location}</p>
              {exp.bullets?.map((b, j) => <p key={j} className="exp-bullet">{highlight(b)}</p>)}
            </div>
          ))}
        </div>
      )}

      {resume.projects?.length > 0 && (
        <div className="structured-section">
          <h3>Projects</h3>
          {resume.projects.map((proj, i) => (
            <div key={i} className="exp-item">
              <div className="flex justify-between items-center">
                <span className="exp-title">{proj.name}</span>
                {proj.link && (
                  <a href={proj.link} target="_blank" rel="noreferrer" style={{ color: "var(--accent3)", fontSize: 11, fontFamily: "var(--font-mono)" }}>
                    Link ↗
                  </a>
                )}
              </div>
              <p style={{ fontSize: 11, color: "var(--text2)", marginBottom: 6, fontFamily: "var(--font-mono)" }}>
                {highlight(proj.tech_stack?.join(", "))}
              </p>
              {proj.bullets?.map((b, j) => <p key={j} className="exp-bullet">{highlight(b)}</p>)}
            </div>
          ))}
        </div>
      )}

      {resume.education?.length > 0 && (
        <div className="structured-section">
          <h3>Education</h3>
          {resume.education.map((edu, i) => (
            <div key={i} className="exp-item">
              <div className="flex justify-between items-center">
                <span className="exp-title">{edu.degree}</span>
                <span style={{ fontSize: 11, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>{edu.graduation_year}</span>
              </div>
              <p className="exp-meta">{edu.institution}</p>
              {edu.gpa && <p className="text-muted text-sm">GPA: {edu.gpa}</p>}
            </div>
          ))}
        </div>
      )}

      {resume.certifications?.length > 0 && (
        <div className="structured-section">
          <h3>Certifications</h3>
          {resume.certifications.map((c, i) => (
            <p key={i} className="text-sm text-muted" style={{ marginBottom: 6 }}>
              {c.name} — {c.issuer} ({c.year})
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
