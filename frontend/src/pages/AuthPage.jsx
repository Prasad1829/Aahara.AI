import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import downVeg from "../assets/down_veg.png";
import googleIcon from "../assets/google.svg";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleError, setGoogleError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    setEmail("");
    setPassword("");
    setGoogleError("");
  }, [mode]);

  useEffect(() => {
    let tries = 0;
    const maxTries = 30;
    const interval = setInterval(() => {
      tries++;
      if (window.google?.accounts?.id) {
        clearInterval(interval);
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: async (response) => {
            setGoogleError("");
            try {
              const res = await fetch(`${API}/auth/google`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id_token: response.credential }),
              });
              const data = await res.json();
              if (!res.ok) {
                setGoogleError(data.detail || "Google login failed.");
                return;
              }
              localStorage.setItem("token", data.access_token);
              localStorage.setItem("user", JSON.stringify(data.user));
              navigate("/dashboard");
            } catch {
              setGoogleError("Google sign-in failed. Please try again.");
            }
          },
        });
      }
      if (tries >= maxTries) {
        clearInterval(interval);
        setGoogleError("Google sign-in unavailable. Check your internet connection.");
      }
    }, 300);
    return () => clearInterval(interval);
  }, []);

  const handleGoogleClick = () => {
    if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          setGoogleError("Google sign-in was blocked. Please allow popups and try again.");
        }
      });
    } else {
      setGoogleError("Google sign-in is still loading. Please try again in a moment.");
    }
  };

  const handle = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === "login") {
        const res = await fetch(`${API}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ username: email, password }),
        });
        const data = await res.json();
        if (!res.ok) { alert(data.detail || "Invalid email or password"); return; }
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify({ email }));
        navigate("/dashboard");
      } else {
        const res = await fetch(`${API}/auth/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (!res.ok) { alert(data.detail || "Registration failed"); return; }
        alert("Registration successful. Please login.");
        setEmail(""); setPassword(""); setMode("login");
      }
    } catch {
      alert("Server error. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container" style={{ background: "#2E8B57" }}>
      <div
        className="page-content page-content--scaled auth-container"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "'DM Sans', sans-serif",
        }}
      >
        <div className="auth-content">
          {/* ✅ CHANGED: image 10% bigger */}
          <img
            src={downVeg}
            alt="Vegetable garnish"
            className="bottom-decor-img"
            loading="lazy"
            style={{
              width: "clamp(462px, 44vw, 770px)",
              transform: "scale(1.10)",
              transformOrigin: "center center",
            }}
          />

          {/* ✅ CHANGED: width 378px, borderRadius 17, marginLeft 40px */}
          <div
            className="auth-card"
            style={{
              background: "rgba(250,246,237,0.98)",
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
              position: "relative",
              zIndex: 2,
              width: "378px",
              maxWidth: "90%",
              padding: "28px 24px",
              borderRadius: "17px",
              marginLeft: "40px",
            }}
          >
            {/* Title — original */}
            <div style={{
              fontFamily: "'Playfair Display', serif",
              fontWeight: 900,
              fontSize: "2.6rem",
              textAlign: "center",
              color: "#2E8B57",
              marginBottom: 4,
            }}>
              Aahara.AI
            </div>

            <p style={{ textAlign: "center", color: "#6b7280", fontSize: "0.85rem", marginBottom: 20 }}>
              Access your recipe assistant
            </p>

            {/* Single tab — original */}
            <div style={{
              background: "#ede9df",
              borderRadius: 12,
              padding: 4,
              marginBottom: 20,
            }}>
              <button style={{
                width: "100%",
                padding: "10px",
                borderRadius: 9,
                border: "none",
                background: "#4a9e6b",
                color: "#fff",
                fontWeight: 700,
                fontSize: "0.88rem",
                cursor: "default",
              }}>
                {mode === "login" ? "Login" : "Register"}
              </button>
            </div>

            {/* Form — original */}
            <form onSubmit={handle}>
              <input
                type="email"
                required
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={inputStyle}
              />
              <input
                type="password"
                required
                placeholder={mode === "login" ? "Enter your password" : "Create a password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ ...inputStyle, marginBottom: 14 }}
              />
              <button
                type="submit"
                disabled={loading}
                style={{
                  width: "100%",
                  padding: "11px 14px",
                  borderRadius: 10,
                  border: "none",
                  background: "#2d2d2d",
                  color: "#fff",
                  fontSize: "0.95rem",
                  fontWeight: 700,
                  cursor: loading ? "not-allowed" : "pointer",
                  opacity: loading ? 0.7 : 1,
                  marginBottom: 14,
                }}
              >
                {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
              </button>
            </form>

            {/* Toggle link — original */}
            <p style={{ textAlign: "center", marginBottom: 14 }}>
              {mode === "login" ? (
                <span
                  onClick={() => setMode("register")}
                  style={{ color: "#2E8B57", fontWeight: 700, fontSize: "0.9rem", cursor: "pointer" }}
                >
                  Create new account
                </span>
              ) : (
                <span
                  onClick={() => setMode("login")}
                  style={{ color: "#2E8B57", fontWeight: 700, fontSize: "0.9rem", cursor: "pointer" }}
                >
                  Back to Login
                </span>
              )}
            </p>

            {/* Divider — original */}
            <div style={{ textAlign: "center", color: "#9ca3af", fontSize: "0.82rem", marginBottom: 14 }}>
              or continue with
            </div>

            {/* Google Button — original */}
            <div style={{ display: "flex", justifyContent: "center", marginBottom: 8 }}>
              <button
                onClick={handleGoogleClick}
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: 14,
                  border: "1.5px solid #e5e7eb",
                  background: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                  transition: "box-shadow 0.2s",
                }}
              >
                <img src={googleIcon} alt="Google" style={{ width: 28, height: 28 }} />
              </button>
            </div>

            {googleError && (
              <p style={{ textAlign: "center", color: "#ef4444", fontSize: "0.82rem", marginTop: 6 }}>
                {googleError}
              </p>
            )}
          </div>
        </div>
      </div>

      <footer className="footer">
        © {new Date().getFullYear()} Aahara.AI · Developed by Vara Prasad · Email:
        <a href="mailto:varaprasad42c4@gmail.com" style={{ marginLeft: 4 }}>
          varaprasad42c4@gmail.com
        </a>{" "}
        · Visakhapatnam
      </footer>
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 10,
  border: "1.5px solid rgba(200,135,58,0.2)",
  background: "#fff",
  fontSize: "0.88rem",
  color: "#2d2d2d",
  outline: "none",
  marginBottom: 12,
  boxSizing: "border-box",
};