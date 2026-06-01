import React from "react";
import ReactDOM from "react-dom/client";
import { Toaster } from "react-hot-toast";
import App from "./App";
import "./App.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
    <Toaster
      position="top-right"
      toastOptions={{
        style: {
          background: "#161720",
          color: "#f1f0ff",
          border: "1px solid rgba(255,255,255,0.1)",
          fontFamily: "'Instrument Sans', sans-serif",
          fontSize: "14px",
          borderRadius: "10px",
          boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
        },
        success: {
          iconTheme: { primary: "#34d399", secondary: "#07080d" },
        },
        error: {
          iconTheme: { primary: "#f87171", secondary: "#07080d" },
        },
      }}
    />
  </React.StrictMode>
);
