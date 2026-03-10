import { useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import { LayoutDashboard, User, History, Settings, LogOut, Heart } from "lucide-react";
import hamburgerIcon from "../assets/hamburger.png";

export default function Navbar({ user }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/auth");
  };

  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { label: "Wishlist",  path: "/wishlist",  icon: Heart },
    { label: "Profile",   path: "/profile",   icon: User },
    { label: "History",   path: "/history",   icon: History },
    { label: "Settings",  path: "/settings",  icon: Settings },
    { label: "Logout",    action: handleLogout, icon: LogOut },
  ];

  return (
    <nav className="dashboard-navbar" style={{
      position: "sticky", top: 0, zIndex: 50,
    }}>
      <div style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: "70px",
        padding: "0 24px",
        position: "relative",
      }}>
        <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
          <button
            onClick={() => setMenuOpen((v) => !v)}
            style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "4px 10px", borderRadius: 10,
              fontSize: "0.58rem", fontWeight: 600,
              background: "transparent",
              color: "#ffffff",
              border: "1px solid transparent",
              cursor: "pointer", transition: "all 0.2s",
            }}
          >
            <img
              src={hamburgerIcon}
              alt="Menu"
              style={{ width: 56, height: 56, objectFit: "contain", display: "block" }}
            />
          </button>

          {menuOpen && (
            <div style={{
              position: "absolute",
              top: "100%",
              left: 0,
              marginTop: 8,
              background: "#2E8B57",
              border: "1px solid rgba(255,255,255,0.25)",
              borderRadius: 10,
              padding: 6,
              display: "flex",
              flexDirection: "column",
              gap: 4,
              zIndex: 60,
            }}>
              {navItems.map(({ label, path, icon: Icon, action }) => {
                const active = path && location.pathname === path;
                return (
                  <button
                    key={label}
                    onClick={() => {
                      setMenuOpen(false);
                      if (action) action();
                      else if (path) navigate(path);
                    }}
                    style={{
                      display: "flex", alignItems: "center", gap: 6,
                      padding: "7px 16px", borderRadius: 10,
                      fontSize: "0.82rem", fontWeight: 600,
                      background: active ? "rgba(255,255,255,0.18)" : "transparent",
                      color: "#ffffff",
                      border: active ? "1px solid rgba(255,255,255,0.35)" : "1px solid transparent",
                      cursor: "pointer", transition: "all 0.2s",
                      textAlign: "left",
                    }}
                  >
                    <Icon size={14} /> {label}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <span
          className="navbar-title"
          onClick={() => navigate("/dashboard")}
          style={{
            fontFamily: '"Playfair Display", Georgia, serif',
            cursor: "pointer",
            position: "absolute",
            left: "50%",
            transform: "translateX(-50%)",
            fontSize: "40px",
          }}
        >
          Aahara.AI
        </span>

        <div />
      </div>
    </nav>
  );
}

