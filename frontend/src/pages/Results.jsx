import React, { useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";

export default function Results({ sessionId, uploadData, onGenerate, onBack }) {
  const [loading, setLoading] = useState(false);
  const { structured, match_result } = uploadData;

  const score      = match_result.ats_score;
  const scoreClass = score >= 70 ? "score-high" : score >= 45 ? "score-mid" : "score-low";
  const scoreLabel = score >= 70 ? "Strong Match" : score >= 45 ? "Moderate Match" : "Low Match";
  const scoreBadge = score >= 70 ? "badge-green" : score >= 45 ? "badge-yellow" : "badge-red";

  async function handleGenerate() {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("session_id", sessionId);
      const res = await axios.post("/api/generate", formData);

      onGenerate({
        tailored_resume:    res.data.tailored_resume,
        latex_code:         res.data.latex_code,
        added_keywords:     res.data.added_keywords     || [],
        new_ats_score:      res.data.new_ats_score      ?? score,
        original_ats_score: res.data.original_ats_score ?? score,
        score_improvement:  res.data.score_improvement  ?? 0,
      });

      toast.success("Resume tailored!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* Header row */}
      <div className="flex items-center gap-3 mb-4">
        <button className="btn btn-ghost btn-sm" onClick={onBack}>← Back</button>
        <div>
          <h1 className="page-title" style={{ fontSize: 28, marginBottom: 0 }}>Resume Analysis</h1>
          <p className="page-subtitle" style={{ marginBottom: 0, fontSize: 14 }}>
            Here's how your resume matches the job description
          </p>
        </div>
        <span className={`badge ${scoreBadge}`} style={{ marginLeft: "auto", fontSize: 12 }}>
          {scoreLabel}
        </span>
      </div>

      <div className="results-grid">
        {/* Left column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* ATS score card */}
          <div className="card ats-score-ring">
            <div style={{
              width: 120, height: 120,
              borderRadius: "50%",
              display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column",
              border: "3px solid",
              marginBottom: 16,
              position: "relative",
            }} className={scoreClass}>
              <span className="score-num">{score}</span>
              <span className="score-label">/ 100</span>
            </div>
            <p style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{scoreLabel}</p>
            <p className="text-muted text-sm" style={{ textAlign: "center", fontFamily: "var(--font-mono)", fontSize: 11 }}>
              ATS Keyword Score
            </p>
          </div>

          {/* Stats card */}
          <div className="card">
            <div className="card-title" style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: "0.08em", textTransform: "uppercase", color: "var(--text3)" }}>Quick Stats</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 11 }}>
              <Stat label="Keywords in JD" value={match_result.total_jd_keywords} />
              <Stat label="Matched"         value={match_result.total_matched}       color="var(--green)" />
              <Stat label="Missing"         value={match_result.missing_keywords?.length} color="var(--red)" />
              <div style={{ height: 1, background: "var(--border)", margin: "2px 0" }} />
              <Stat label="Skills Found"    value={structured.skills?.technical?.length || 0} />
              <Stat label="Experience"      value={`${structured.experience?.length || 0} roles`} />
              <Stat label="Projects"        value={structured.projects?.length || 0} />
            </div>
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Recommendations */}
          <div className="card">
            <div className="card-title">💡 Recommendations</div>
            <ul className="recs-list">
              {match_result.recommendations?.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>

          {/* Keyword match */}
          <div className="card">
            <div className="card-title">Keyword Match Analysis</div>
            <p className="text-muted text-sm" style={{ marginBottom: 14, fontFamily: "var(--font-mono)", fontSize: 11 }}>
              <span style={{ color: "#6ee7b7" }}>■</span> Found in resume &nbsp;
              <span style={{ color: "#fca5a5" }}>■</span> Missing from resume
            </p>
            <div className="keywords-grid">
              {match_result.matched_keywords?.map((kw) => (
                <span key={kw} className="tag tag-match">{kw}</span>
              ))}
              {match_result.missing_keywords?.map((kw) => (
                <span key={kw} className="tag tag-missing">{kw}</span>
              ))}
            </div>
          </div>

          {/* Detected profile */}
          <div className="card">
            <div className="card-title">Detected Profile</div>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 14 }}>
              <div>
                <p style={{ fontSize: 17, fontWeight: 700, fontFamily: "var(--font-head)", letterSpacing: "-0.3px" }}>{structured.name}</p>
                <p className="text-muted text-sm" style={{ fontFamily: "var(--font-mono)", fontSize: 12, marginTop: 3 }}>{structured.email}</p>
                {structured.location && (
                  <p className="text-muted text-sm" style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{structured.location}</p>
                )}
              </div>
            </div>
            {structured.skills?.technical?.length > 0 && (
              <div>
                <p style={{ fontSize: 11, color: "var(--text3)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>Top Skills</p>
                <div>
                  {structured.skills.technical.slice(0, 10).map((s) => (
                    <span key={s} className="tag">{s}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* CTA */}
          <button
            className="btn btn-primary btn-lg"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                Tailoring your resume...
              </>
            ) : (
              "Generate Tailored Resume →"
            )}
          </button>
          {loading && (
            <p className="text-muted text-sm" style={{ fontFamily: "var(--font-mono)", fontSize: 12, textAlign: "center" }}>
              Injecting missing keywords — takes 15–30 seconds
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, color }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-muted text-sm">{label}</span>
      <span style={{ fontWeight: 700, color: color || "var(--text)", fontSize: 15, fontFamily: "var(--font-mono)" }}>
        {value}
      </span>
    </div>
  );
}
