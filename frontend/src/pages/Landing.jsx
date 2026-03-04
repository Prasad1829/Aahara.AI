import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

export default function LandingPage() {
  const navigate = useNavigate();
  const showIntro = false;
  const fadeIn = true;

  return (
    <div style={{ minHeight: "100vh", background: "#F5EFE6" }}>
      {/* Header */}
      <header
        style={{
          padding: "18px 24px",
          borderBottom: "1px solid rgba(0,0,0,0.06)",
          background: "rgba(245,239,230,0.85)",
          backdropFilter: "blur(10px)",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div
          style={{
            maxWidth: 1100,
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          <div />

          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <button
              onClick={() => navigate("/auth")}
              style={{
                padding: "10px 14px",
                borderRadius: 999,
                border: "1px solid rgba(0,0,0,0.12)",
                background: "transparent",
                cursor: "pointer",
                fontWeight: 700,
                color: "#374151",
              }}
            >
              Sign in
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main
        className={fadeIn ? "opacity-0 animate-[fadeIn_300ms_ease-out_forwards]" : ""}
        style={{ display: "grid", placeItems: "center", padding: "34px 18px" }}
      >
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{
          opacity: showIntro ? 0 : 1,
          scale: showIntro ? 0.9 : 1,
          y: showIntro ? 20 : 0,
        }}
        transition={{ duration: 0.7, ease: "easeOut" }}
        style={{
          width: "min(520px, 92vw)",
          textAlign: "center",
          pointerEvents: showIntro ? "none" : "auto",
        }}
      >
        <div
          style={{
            fontFamily: "'Playfair Display', serif",
            fontWeight: 900,
            fontSize: "2.2rem",
            color: "#111827",
            marginBottom: 10,
          }}
        >
          Welcome to Aahara.AI
        </div>
        <div style={{ color: "#6b7280", marginBottom: 26 }}>
          Personalized Nutrition at Your Fingertips
        </div>

        {/* Icon buttons */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: 32,
            marginBottom: 28,
          }}
        >
          {[
            { icon: "📷", label: "Scan", bg: "#d1fae5", color: "#059669" },
            { icon: "👨‍🍳", label: "Cook", bg: "#fef3c7", color: "#d97706" },
          ].map((item) => (
            <div key={item.label} style={{ textAlign: "center" }}>
              <div
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: "50%",
                  background: item.bg,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "1.6rem",
                  marginBottom: 8,
                  boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
                }}
              >
                {item.icon}
              </div>
              <div
                style={{
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  color: "#4b5563",
                }}
              >
                {item.label}
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={() => navigate("/auth")}
          style={{
            padding: "14px 22px",
            borderRadius: 999,
            border: "none",
            background: "#4a9e6b",
            color: "#fff",
            fontSize: "1rem",
            fontWeight: 800,
            cursor: "pointer",
            boxShadow: "0 10px 22px rgba(74,158,107,0.25)",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "#3d8a5c")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "#4a9e6b")}
        >
          Get started
        </button>
      </motion.div>
      </main>

      {/* Footer – compact */}
      <footer
        style={{
          padding: "10px 16px",
          borderTop: "1px solid rgba(0,0,0,0.05)",
          color: "#6B7280",
          fontSize: "0.8rem",
        }}
      >
        <div
          style={{
            maxWidth: 1100,
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 8,
            flexWrap: "wrap",
          }}
        >
          <div>
            © {new Date().getFullYear()} Aahara. Developed by <strong>Vara Prasad</strong> · Email:
            <span style={{ marginLeft: 4 }}>varaprasad42c4</span> · Visakhapatnam
          </div>
        </div>
      </footer>
    </div>
  );
}