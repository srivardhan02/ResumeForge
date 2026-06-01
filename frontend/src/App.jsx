import React, { useState } from "react";
import Upload from "./pages/Upload";
import Results from "./pages/Results";
import Editor from "./pages/Editor";
import "./App.css";

export default function App() {
  const [page, setPage] = useState("upload"); // upload | results | editor
  const [sessionId, setSessionId] = useState(null);
  const [uploadData, setUploadData] = useState(null);
  const [resumeData, setResumeData] = useState(null);

  function handleUploadComplete(sessionId, data) {
    setSessionId(sessionId);
    setUploadData(data);
    setPage("results");
  }

  function handleGenerateComplete(data) {
    setResumeData(data);
    setPage("editor");
  }

  function handleStartOver() {
    setPage("upload");
    setSessionId(null);
    setUploadData(null);
    setResumeData(null);
  }

  return (
    <div className="app">
      <Header currentPage={page} onStartOver={handleStartOver} />
      <main className="main-content">
        {page === "upload" && (
          <Upload onComplete={handleUploadComplete} />
        )}
        {page === "results" && (
          <Results
            sessionId={sessionId}
            uploadData={uploadData}
            onGenerate={handleGenerateComplete}
            onBack={() => setPage("upload")}
          />
        )}
        {page === "editor" && (
          <Editor
            sessionId={sessionId}
            resumeData={resumeData}
            onResumeUpdate={setResumeData}
            onBack={() => setPage("results")}
          />
        )}
      </main>
    </div>
  );
}

function Header({ currentPage, onStartOver }) {
  const steps = [
    { id: "upload",  label: "Upload" },
    { id: "results", label: "Analysis" },
    { id: "editor",  label: "Editor" },
  ];

  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo" onClick={onStartOver} title="Start over">
          <span className="logo-icon">⬡</span>
          <span className="logo-text">ResumeForge</span>
        </div>
        <nav className="steps-nav">
          {steps.map((step, i) => (
            <React.Fragment key={step.id}>
              <div
                className={`step ${currentPage === step.id ? "active" : ""} ${
                  steps.findIndex((s) => s.id === currentPage) > i ? "done" : ""
                }`}
              >
                <span className="step-num">
                  {steps.findIndex((s) => s.id === currentPage) > i ? "✓" : i + 1}
                </span>
                <span className="step-label">{step.label}</span>
              </div>
              {i < steps.length - 1 && <div className="step-line" />}
            </React.Fragment>
          ))}
        </nav>
      </div>
    </header>
  );
}
