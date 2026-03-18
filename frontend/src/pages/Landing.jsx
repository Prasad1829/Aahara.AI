import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import leftVeg from "../assets/left_veg.png";
import rightVeg from "../assets/right_veg.png";

export default function LandingPage() {
  const navigate = useNavigate();
  const showIntro = false;
  const fadeIn = false;

  return (
    <div className="page-container" style={{ background: "#2E8B57" }}>
      <div className="page-content">
        <div className="hero-section">
          <img
            src={leftVeg}
            alt="Fresh vegetables"
            className="hero-left-img"
            loading="lazy"
          />

          <div className="hero-content">
            <main
              className={fadeIn ? "opacity-0 animate-[fadeIn_300ms_ease-out_forwards]" : ""}
              style={{
                display: "grid",
                placeItems: "center",
                padding: "34px 18px",
                minHeight: "calc(100vh - 140px)",
              }}
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.96, y: 16 }}
                animate={{
                  opacity: showIntro ? 0 : 1,
                  scale: showIntro ? 0.96 : 1,
                  y: showIntro ? 16 : 0,
                }}
                transition={{ duration: 0.7, ease: "easeOut" }}
                style={{
                  width: "min(506px, 90vw)",
                  textAlign: "center",
                  pointerEvents: showIntro ? "none" : "auto",
                  background: "#ffffff",
                  border: "1px solid rgba(0,0,0,0.06)",
                  borderRadius: 24,
                  padding: "37px 31px",
                  boxShadow: "0 18px 40px rgba(0,0,0,0.25)",
                }}
              >
                <div
                  style={{
                    fontFamily: "'Playfair Display', serif",
                    fontWeight: 900,
                    fontSize: "2.42rem",
                    color: "#1f2937",
                    marginBottom: 11,
                  }}
                >
                  Welcome to Aahara.AI
                </div>
                <div style={{ color: "#6b7280", marginBottom: 29, fontSize: "1.1rem" }}>
                  Personalized Nutrition at Your Fingertips
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    gap: 35,
                    marginBottom: 31,
                  }}
                >
                  {[
                    { icon: "📷", label: "Scan", bg: "#d1fae5", color: "#059669" },
                    { icon: "👨‍🍳", label: "Cook", bg: "#fef3c7", color: "#d97706" },
                  ].map((item) => (
                    <div key={item.label} style={{ textAlign: "center" }}>
                      <div
                        style={{
                          width: 70,
                          height: 70,
                          borderRadius: "50%",
                          background: item.bg,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "1.76rem",
                          marginBottom: 9,
                          boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
                        }}
                      >
                        {item.icon}
                      </div>
                      <div
                        style={{
                          fontSize: "0.94rem",
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
                    padding: "15px 24px",
                    borderRadius: 999,
                    border: "none",
                    background: "#C8A24A",
                    color: "#1f2937",
                    fontSize: "1.1rem",
                    fontWeight: 800,
                    cursor: "pointer",
                    boxShadow: "0 10px 22px rgba(0,0,0,0.2)",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "#B08D3F")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "#C8A24A")}
                >
                  Get started
                </button>
              </motion.div>
            </main>
          </div>

          <img
            src={rightVeg}
            alt="Plated food"
            className="hero-right-img"
            loading="lazy"
          />
        </div>
      </div>

      <footer className="footer" style={{ marginTop: 0 }}>
        © {new Date().getFullYear()} Aahara.AI · Developed by Vara Prasad · Email:
        <a href="mailto:varaprasad42c4@gmail.com" style={{ marginLeft: 4 }}>
          varaprasad42c4@gmail.com
        </a>{" "}
        · Visakhapatnam
      </footer>
    </div>
  );
}