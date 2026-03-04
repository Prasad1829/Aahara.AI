import { useNavigate, useLocation } from "react-router-dom";
import { LayoutDashboard, User, History, Settings, LogOut } from "lucide-react";

export default function Navbar({ user }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/auth");
  };

  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { label: "Profile",   path: "/profile",   icon: User },
    { label: "History",   path: "/history",   icon: History },
    { label: "Settings",  path: "/settings",  icon: Settings },
  ];

  return (
    <nav style={{
      position: "sticky", top: 0, zIndex: 50,
      background: "rgba(250,246,237,0.97)",
      borderBottom: "1px solid rgba(200,135,58,0.2)",
      backdropFilter: "blur(12px)",
    }}>
      <div style={{
        maxWidth: 1200, margin: "0 auto",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "12px 24px",
      }}>
        <span onClick={() => navigate("/dashboard")} style={{
          fontFamily: '"Playfair Display", Georgia, serif',
          fontWeight: 900, fontSize: "1.4rem",
          color: "#C8873A", cursor: "pointer",
        }}>
          Aahara.AI
        </span>

        <div style={{ display: "flex", gap: 4 }}>
          {navItems.map(({ label, path, icon: Icon }) => {
            const active = location.pathname === path;
            return (
              <button key={path} onClick={() => navigate(path)} style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "7px 16px", borderRadius: 10,
                fontSize: "0.82rem", fontWeight: 600,
                background: active ? "rgba(74,158,107,0.12)" : "transparent",
                color: active ? "#4a9e6b" : "#6b7280",
                border: active ? "1px solid rgba(74,158,107,0.3)" : "1px solid transparent",
                cursor: "pointer", transition: "all 0.2s",
              }}
              onMouseEnter={(e) => { if (!active) e.currentTarget.style.color = "#C8873A"; }}
              onMouseLeave={(e) => { if (!active) e.currentTarget.style.color = "#6b7280"; }}
              >
                <Icon size={14} /> {label}
              </button>
            );
          })}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: "0.8rem", color: "#9ca3af" }}>{user?.email}</span>
          <button onClick={handleLogout} style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "7px 14px", borderRadius: 10,
            fontSize: "0.82rem", fontWeight: 600,
            color: "#6b7280", background: "transparent",
            border: "1px solid rgba(0,0,0,0.1)", cursor: "pointer",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "#ef4444")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "#6b7280")}
          >
            <LogOut size={14} /> Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
