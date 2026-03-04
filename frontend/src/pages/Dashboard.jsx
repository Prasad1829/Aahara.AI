import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Upload, Salad, PenLine } from "lucide-react";
import Navbar from "../components/Navbar";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const BG = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) { navigate("/auth"); return; }
    fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json()).then(setUser).catch(() => {});
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
    <div style={{ minHeight: "100vh", position: "relative" }}>
      {/* Same food photo background as landing/auth */}
      <div style={{
        position: "fixed", inset: 0,
        backgroundImage: `linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.6)), url('${BG}')`,
        backgroundSize: "cover", backgroundPosition: "center", zIndex: 0,
      }} />
      <div style={{ position: "relative", zIndex: 1 }}>
        <Navbar user={user} />
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "60px 24px" }}>

          {/* Header card — same cream style */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            style={{ textAlign: "center", marginBottom: 48,
              background: "rgba(250,246,237,0.95)", borderRadius: 24,
              padding: "36px 32px", backdropFilter: "blur(8px)" }}>
            <p style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase",
              letterSpacing: "0.15em", color: "#4a9e6b", marginBottom: 10 }}>
              Welcome back{user?.email ? `, ${user.email.split("@")[0]}` : ""}
            </p>
            <h1 style={{ fontFamily: '"Playfair Display", Georgia, serif',
              fontSize: "3rem", fontWeight: 900, color: "#2d2d2d", lineHeight: 1.15, marginBottom: 12 }}>
              What's in your Kitchen?
            </h1>
            <p style={{ color: "#6b7280", fontSize: "1rem" }}>
              Choose how you'd like to add your ingredients and we'll find the perfect recipe.
            </p>
          </motion.div>

          {/* Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20 }}>
            {options.map((opt, i) => {
              const Icon = opt.icon;
              return (
                <motion.div key={opt.route}
                  initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                  whileHover={{ scale: 1.03, y: -4 }} whileTap={{ scale: 0.98 }}
                  onClick={() => navigate(opt.route)}
                  style={{ background: "rgba(250,246,237,0.95)", borderRadius: 22,
                    padding: "28px 24px", cursor: "pointer",
                    border: `1px solid ${opt.border}`,
                    backdropFilter: "blur(8px)", transition: "all 0.3s" }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = `0 16px 48px ${opt.glow}`;
                    e.currentTarget.style.border = `1px solid ${opt.color}`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = "none";
                    e.currentTarget.style.border = `1px solid ${opt.border}`;
                  }}>
                  <span style={{ display: "inline-block", borderRadius: 20, padding: "4px 12px",
                    fontSize: "0.72rem", fontWeight: 700, marginBottom: 20,
                    background: opt.iconBg, color: opt.color }}>
                    {opt.tag}
                  </span>
                  <div style={{ width: 60, height: 60, borderRadius: 16, background: opt.iconBg,
                    display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
                    <Icon size={26} style={{ color: opt.color }} />
                  </div>
                  <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#2d2d2d", marginBottom: 8 }}>
                    {opt.title}
                  </h2>
                  <p style={{ fontSize: "0.85rem", color: "#6b7280", lineHeight: 1.6 }}>{opt.desc}</p>
                  <div style={{ marginTop: 24, fontSize: "0.85rem", fontWeight: 700,
                    color: opt.color, display: "flex", alignItems: "center", gap: 6 }}>
                    Get Started →
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
