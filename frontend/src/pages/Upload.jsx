import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import toast from "react-hot-toast";

export default function Upload({ onComplete }) {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      setFile(accepted[0]);
      toast.success(`Loaded: ${accepted[0].name}`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    maxFiles: 1,
  });

  async function handleSubmit() {
    if (!file) return toast.error("Please upload your resume");
    if (!jobDescription.trim()) return toast.error("Please paste the job description");
    if (jobDescription.trim().length < 50)
      return toast.error("Job description seems too short — paste the full JD");

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("resume", file);
      formData.append("job_description", jobDescription);

      const res = await axios.post("/api/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      onComplete(res.data.session_id, {
        structured: res.data.structured,
        match_result: res.data.match_result,
      });
    } catch (err) {
      const msg = err.response?.data?.detail || "Upload failed. Check your API key and try again.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="upload-page">
      {/* Hero text */}
      <div style={{ marginBottom: 48 }}>
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          background: "var(--accent-glow2)",
          border: "1px solid rgba(99,102,241,0.2)",
          borderRadius: 20,
          padding: "4px 14px",
          marginBottom: 20,
          fontSize: 12,
          fontFamily: "var(--font-mono)",
          color: "var(--accent3)",
          letterSpacing: "0.05em",
        }}>
          <span style={{ color: "var(--green)", fontSize: 8 }}>●</span>
          AI-POWERED · ATS OPTIMIZED
        </div>
        <h1 className="page-title">Forge Your Resume</h1>
        <p className="page-subtitle">
          Upload your resume and paste a job description.<br />
          We'll tailor it with precision-injected keywords.
        </p>
      </div>

      {/* Step 1 — Resume upload */}
      <div style={{ marginBottom: 8, display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{
          width: 22, height: 22, borderRadius: "50%",
          background: "var(--accent)", color: "#fff",
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          fontSize: 11, fontWeight: 700, fontFamily: "var(--font-mono)", flexShrink: 0,
        }}>1</span>
        <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text2)" }}>Upload your resume</span>
      </div>

      <div {...getRootProps()} className={`dropzone ${isDragActive ? "active" : ""}`}>
        <input {...getInputProps()} />
        <div className="dropzone-icon">{isDragActive ? "📂" : "📄"}</div>
        <p className="dropzone-text">
          {isDragActive ? (
            "Drop it here"
          ) : (
            <><strong>Drag & drop</strong> your resume or click to browse</>
          )}
        </p>
        <p className="dropzone-hint">PDF · DOCX · TXT</p>
      </div>

      {file && (
        <div className="file-selected">
          <span style={{ fontSize: 16 }}>✅</span>
          <span style={{ fontWeight: 600, fontSize: 14 }}>{file.name}</span>
          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--text3)", fontFamily: "var(--font-mono)" }}>
            {(file.size / 1024).toFixed(0)} KB
          </span>
          <button
            onClick={(e) => { e.stopPropagation(); setFile(null); }}
            style={{ background: "none", border: "none", cursor: "pointer", color: "var(--red)", fontSize: 18, lineHeight: 1, padding: "0 2px" }}
          >
            ×
          </button>
        </div>
      )}

      {/* Step 2 — Job description */}
      <div style={{ marginBottom: 8, marginTop: 24, display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{
          width: 22, height: 22, borderRadius: "50%",
          background: "var(--accent)", color: "#fff",
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          fontSize: 11, fontWeight: 700, fontFamily: "var(--font-mono)", flexShrink: 0,
        }}>2</span>
        <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text2)" }}>Paste the job description</span>
      </div>

      <textarea
        className="jd-textarea"
        placeholder="Paste the full job description here — requirements, responsibilities, about the role, everything..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />

      <button
        className="btn btn-primary btn-lg w-full"
        onClick={handleSubmit}
        disabled={loading || !file || !jobDescription.trim()}
        style={{ marginTop: 4 }}
      >
        {loading ? (
          <>
            <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
            Analyzing your resume...
          </>
        ) : (
          "Analyze & Continue →"
        )}
      </button>

      {loading && (
        <p className="text-muted text-sm" style={{ marginTop: 12, textAlign: "center", fontFamily: "var(--font-mono)", fontSize: 12 }}>
          Parsing resume · Matching keywords · Building analysis — ~15s
        </p>
      )}
    </div>
  );
}
