import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Upload, Salad, PenLine } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
export default function Dashboard() {
  const [, setUser] = useState(null);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) { navigate("/auth"); return; }
    fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => { setUser(data); })
      .catch(() => {});
  }, []);

  const options = [
    {
      title: "Upload Image",
      desc: "Take a photo or upload an image of your ingredients. Our AI will identify them instantly.",
      icon: Upload, route: "/upload-image",
      color: "#4a9e6b", bg: "rgba(74,158,107,0.1)",
      border: "rgba(74,158,107,0.3)", glow: "rgba(74,158,107,0.25)",
      iconBg: "rgba(74,158,107,0.15)", tag: "AI Powered",
    },
    {
      title: "Select Vegetables",
      desc: "Browse our visual vegetable library and tap to select what you have in your kitchen.",
      icon: Salad, route: "/select-vegetables",
      color: "#C8873A", bg: "rgba(200,135,58,0.1)",
      border: "rgba(200,135,58,0.3)", glow: "rgba(200,135,58,0.25)",
      iconBg: "rgba(200,135,58,0.15)", tag: "Visual Pick",
    },
    {
      title: "Manual Entry",
      desc: "Know your ingredients? Type them in directly and get recipe suggestions in seconds.",
      icon: PenLine, route: "/manual-entry",
      color: "#7c6a52", bg: "rgba(124,106,82,0.1)",
      border: "rgba(124,106,82,0.3)", glow: "rgba(124,106,82,0.25)",
      iconBg: "rgba(124,106,82,0.15)", tag: "Quick Entry",
    },
  ];

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "14px 24px 24px" }}>
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
        style={{ textAlign: "center", marginBottom: 12,
          background: "rgba(250,246,237,0.95)", borderRadius: 22,
          padding: "14px 18px", backdropFilter: "blur(8px)" }}>
        <p style={{ fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase",
          letterSpacing: "0.15em", color: "#4a9e6b", marginBottom: 6 }}>
          Welcome
        </p>
        <h1 style={{ fontFamily: '"Playfair Display", Georgia, serif',
          fontSize: "1.8rem", fontWeight: 900, color: "#2d2d2d", lineHeight: 1.1, marginBottom: 8 }}>
          What's in your Kitchen?
        </h1>
        <p style={{ color: "#6b7280", fontSize: "0.9rem", margin: 0 }}>
          Choose how you'd like to add your ingredients and we'll find the perfect recipe.
        </p>
      </motion.div>

      <div className="cards-container" style={{ marginTop: 10 }}>
        {options.map((opt, i) => {
          const Icon = opt.icon;
          return (
            <motion.div key={opt.route}
              initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              whileHover={{ scale: 1.05, y: -8 }} whileTap={{ scale: 0.98 }}
              onClick={() => navigate(opt.route)}
              className="feature-card"
              style={{ background: "rgba(250,246,237,0.95)",
                cursor: "pointer",
                border: `1px solid ${opt.border}`,
                backdropFilter: "blur(8px)", transition: "all 0.3s" }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = `0 20px 60px ${opt.glow}`;
                e.currentTarget.style.border = `1px solid ${opt.color}`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = "none";
                e.currentTarget.style.border = `1px solid ${opt.border}`;
              }}>
              <span style={{ display: "inline-block", borderRadius: 20, padding: "4px 12px",
                fontSize: "0.72rem", fontWeight: 700, marginBottom: 14,
                background: opt.iconBg, color: opt.color }}>
                {opt.tag}
              </span>
              <div style={{ width: 46, height: 46, borderRadius: 12, background: opt.iconBg,
                display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 12 }}>
                <Icon size={20} style={{ color: opt.color }} />
              </div>
              <h2 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#2d2d2d", marginBottom: 6 }}>
                {opt.title}
              </h2>
              <p style={{ fontSize: "0.78rem", color: "#6b7280", lineHeight: 1.5 }}>{opt.desc}</p>
              <div style={{ marginTop: 14, fontSize: "0.78rem", fontWeight: 700,
                color: opt.color, display: "flex", alignItems: "center", gap: 6 }}>
                Get Started →
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}