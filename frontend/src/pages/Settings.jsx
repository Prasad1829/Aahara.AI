import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const SETTINGS_KEY = "ahara_settings";

const CARD = {
  background: "rgba(250,246,237,0.97)",
  borderRadius: 24,
  padding: 24,
  backdropFilter: "blur(10px)",
  border: "1px solid rgba(120,113,108,0.14)",
  boxShadow: "0 22px 60px rgba(28,25,23,0.08)",
};

const inputStyle = {
  width: "100%",
  padding: "12px 14px",
  borderRadius: 14,
  border: "1px solid rgba(120,113,108,0.2)",
  background: "#fff",
  color: "#1c1917",
  fontSize: "0.95rem",
  outline: "none",
  boxSizing: "border-box",
};

const toggleTrack = (enabled) => ({
  width: 56,
  height: 32,
  borderRadius: 999,
  border: "none",
  cursor: "pointer",
  background: enabled ? "#15803d" : "#d6d3d1",
  padding: 4,
  transition: "background 0.2s ease",
  display: "flex",
  alignItems: "center",
  justifyContent: enabled ? "flex-end" : "flex-start",
});

function ToggleRow({ title, description, value, onChange }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 18,
        padding: "16px 0",
        borderBottom: "1px solid rgba(120,113,108,0.12)",
      }}
    >
      <div>
        <div style={{ fontWeight: 700, color: "#1c1917" }}>{title}</div>
        <div style={{ color: "#6b7280", fontSize: "0.9rem", marginTop: 4 }}>{description}</div>
      </div>
      <button type="button" aria-pressed={value} onClick={() => onChange(!value)} style={toggleTrack(value)}>
        <span
          style={{
            width: 24,
            height: 24,
            borderRadius: "50%",
            background: "#fff",
            boxShadow: "0 4px 12px rgba(0,0,0,0.12)",
          }}
        />
      </button>
    </div>
  );
}

function SectionTitle({ eyebrow, title, description }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <p
        style={{
          margin: 0,
          color: "#15803d",
          fontSize: "0.78rem",
          fontWeight: 800,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
        }}
      >
        {eyebrow}
      </p>
      <h2 style={{ margin: "8px 0 6px", color: "#1c1917", fontSize: "1.4rem" }}>{title}</h2>
      <p style={{ margin: 0, color: "#6b7280" }}>{description}</p>
    </div>
  );
}

export default function Settings() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: false,
    language: "English",
    region: "India",
    activityVisible: true,
  });
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (stored) {
        setSettings((current) => ({ ...current, ...JSON.parse(stored) }));
      }
    } catch {
      // Ignore malformed local storage and continue with defaults.
    }
  }, []);

  const persistSettings = (nextSettings) => {
    setSettings(nextSettings);
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(nextSettings));
    setError("");
  };

  const updateField = (key, value) => {
    persistSettings({ ...settings, [key]: value });
  };

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm("Are you sure you want to permanently delete your account?");
    if (!confirmed) {
      return;
    }

    setDeleting(true);
    setError("");

    try {
      const response = await fetch(`${API}/auth/account`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
        },
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Could not delete account.");
      }

      localStorage.removeItem("token");
      localStorage.removeItem("user");
      localStorage.removeItem(SETTINGS_KEY);
      navigate("/auth", { replace: true });
    } catch (deleteError) {
      setError(deleteError.message || "Could not delete account.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "40px 24px 80px", display: "grid", gap: 22 }}>
      <div style={CARD}>
        <div style={{ marginBottom: 18 }}>
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            style={{
              border: "1px solid rgba(120,113,108,0.2)",
              borderRadius: 14,
              padding: "10px 16px",
              background: "#fff",
              color: "#292524",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Back
          </button>
        </div>

        {error ? (
          <div style={{ marginBottom: 6, padding: "10px 12px", borderRadius: 12, background: "#fef2f2", color: "#b91c1c", border: "1px solid #fecaca", fontSize: "0.92rem" }}>
            {error}
          </div>
        ) : null}

        <ToggleRow
          title="Email Notifications"
          description="Receive recipe alerts and important updates by email."
          value={settings.emailNotifications}
          onChange={(value) => updateField("emailNotifications", value)}
        />
        <ToggleRow
          title="Push Notifications"
          description="Get quick updates and reminders directly in the app."
          value={settings.pushNotifications}
          onChange={(value) => updateField("pushNotifications", value)}
        />

        <div style={{ marginTop: 28, paddingTop: 8 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 18 }}>
            <label style={{ display: "grid", gap: 8, maxWidth: 320 }}>
              <span style={{ color: "#44403c", fontSize: "0.92rem", fontWeight: 700 }}>Region</span>
              <select value={settings.region} onChange={(event) => updateField("region", event.target.value)} style={inputStyle}>
                <option>India</option>
                <option>US</option>
                <option>UK</option>
                <option>Australia</option>
              </select>
            </label>
          </div>
        </div>

        <div style={{ marginTop: 28, paddingTop: 8 }}>
          <SectionTitle
            eyebrow="Delete Account"
            title="Permanently remove your account"
            description="This action deletes your profile data and cannot be undone."
          />
          <button
            type="button"
            onClick={handleDeleteAccount}
            disabled={deleting}
            style={{
              border: "none",
              borderRadius: 14,
              padding: "12px 18px",
              background: "#dc2626",
              color: "#fff",
              fontWeight: 700,
              cursor: deleting ? "not-allowed" : "pointer",
              opacity: deleting ? 0.7 : 1,
            }}
          >
            {deleting ? "Deleting..." : "Delete Account"}
          </button>
        </div>
      </div>
    </div>
  );
}
