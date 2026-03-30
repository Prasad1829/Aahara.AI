import { ArrowLeft } from "lucide-react";

export default function ActionPageHeader({ title, subtitle, onBack }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <button
        type="button"
        onClick={onBack}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          fontSize: "0.82rem",
          color: "#2d2d2d",
          background: "#fff",
          border: "1px solid rgba(255,255,255,0.95)",
          borderRadius: 999,
          padding: "10px 14px",
          cursor: "pointer",
          boxShadow: "0 8px 20px rgba(0,0,0,0.12)",
        }}
      >
        <ArrowLeft size={15} /> Back to Dashboard
      </button>

      <div style={{ marginTop: 18 }}>
        <h1
          style={{
            margin: 0,
            color: "#fffaf0",
            fontSize: "1.8rem",
            fontWeight: 800,
            fontFamily: '"Playfair Display", Georgia, serif',
          }}
        >
          {title}
        </h1>
        <p style={{ margin: "6px 0 0", color: "rgba(255,255,255,0.78)", fontSize: "0.92rem" }}>
          {subtitle}
        </p>
      </div>
    </div>
  );
}
