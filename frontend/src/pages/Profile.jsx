import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const cardStyle = {
  background: "rgba(250, 246, 237, 0.96)",
  borderRadius: 28,
  border: "1px solid rgba(120, 113, 108, 0.14)",
  boxShadow: "0 28px 70px rgba(41, 37, 36, 0.12)",
  backdropFilter: "blur(16px)",
};

function getInitials(fullName, email) {
  const source = (fullName || email || "").trim();
  if (!source) {
    return "U";
  }

  const parts = source.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }

  return source.slice(0, 2).toUpperCase();
}

function absoluteAvatarUrl(avatarUrl) {
  if (!avatarUrl) {
    return "";
  }
  if (avatarUrl.startsWith("http://") || avatarUrl.startsWith("https://")) {
    return avatarUrl;
  }
  return `${API}${avatarUrl}`;
}

function Field({ label, children, note }) {
  return (
    <label style={{ display: "grid", gap: 8 }}>
      <span style={{ color: "#44403c", fontSize: "0.92rem", fontWeight: 700 }}>{label}</span>
      {children}
      {note ? <span style={{ color: "#78716c", fontSize: "0.8rem" }}>{note}</span> : null}
    </label>
  );
}

function Message({ tone = "neutral", children }) {
  const tones = {
    neutral: { color: "#57534e", background: "#f5f5f4", border: "1px solid #e7e5e4" },
    success: { color: "#166534", background: "#ecfdf5", border: "1px solid #bbf7d0" },
    error: { color: "#b91c1c", background: "#fef2f2", border: "1px solid #fecaca" },
  };

  return (
    <div
      style={{
        ...tones[tone],
        borderRadius: 14,
        padding: "12px 14px",
        fontSize: "0.92rem",
      }}
    >
      {children}
    </div>
  );
}

function PasswordModal({ open, onClose, onSubmit, loading, errorMessage, successMessage }) {
  const [form, setForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  useEffect(() => {
    if (open) {
      setForm({ current_password: "", new_password: "", confirm_password: "" });
    }
  }, [open]);

  if (!open) {
    return null;
  }

  const handleChange = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(form);
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(28, 25, 23, 0.55)",
        backdropFilter: "blur(4px)",
        display: "grid",
        placeItems: "center",
        padding: 20,
        zIndex: 1000,
      }}
    >
      <div
        style={{
          width: "min(100%, 460px)",
          background: "#fffaf2",
          borderRadius: 24,
          boxShadow: "0 30px 90px rgba(28, 25, 23, 0.25)",
          padding: 24,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 18 }}>
          <div>
            <h2 style={{ margin: 0, color: "#1c1917", fontSize: "1.35rem" }}>Change Password</h2>
            <p style={{ margin: "8px 0 0", color: "#78716c", fontSize: "0.92rem" }}>
              Enter your current password and choose a new secure one.
            </p>
          </div>
          <button type="button" onClick={onClose} style={secondaryButtonStyle}>
            Close
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 14 }}>
          <Field label="Current Password">
            <input
              type="password"
              value={form.current_password}
              onChange={(event) => handleChange("current_password", event.target.value)}
              style={inputStyle}
              required
            />
          </Field>

          <Field label="New Password" note="Use at least 6 characters.">
            <input
              type="password"
              value={form.new_password}
              onChange={(event) => handleChange("new_password", event.target.value)}
              style={inputStyle}
              required
            />
          </Field>

          <Field label="Confirm New Password">
            <input
              type="password"
              value={form.confirm_password}
              onChange={(event) => handleChange("confirm_password", event.target.value)}
              style={inputStyle}
              required
            />
          </Field>

          {errorMessage ? <Message tone="error">{errorMessage}</Message> : null}
          {successMessage ? <Message tone="success">{successMessage}</Message> : null}

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 6 }}>
            <button type="button" onClick={onClose} style={secondaryButtonStyle}>
              Cancel
            </button>
            <button type="submit" disabled={loading} style={primaryButtonStyle}>
              {loading ? "Updating..." : "Update Password"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Profile() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const storedUser = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "{}");
    } catch {
      return {};
    }
  }, []);

  const [profile, setProfile] = useState({
    email: storedUser.email || "",
    full_name: storedUser.full_name || "",
    phone_number: storedUser.phone_number || "",
    avatar_url: storedUser.avatar_url || "",
  });
  const [draft, setDraft] = useState({
    full_name: storedUser.full_name || "",
    phone_number: storedUser.phone_number || "",
  });
  const [pageLoading, setPageLoading] = useState(true);
  const [savingDetails, setSavingDetails] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [detailsError, setDetailsError] = useState("");
  const [detailsSuccess, setDetailsSuccess] = useState("");
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");

  useEffect(() => {
    if (!detailsSuccess) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setDetailsSuccess("");
    }, 1000);

    return () => window.clearTimeout(timeoutId);
  }, [detailsSuccess]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setPageLoading(false);
      return;
    }

    const loadProfile = async () => {
      try {
        const response = await fetch(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "Failed to load profile.");
        }

        setProfile(data);
        setDraft({
          full_name: data.full_name || "",
          phone_number: data.phone_number || "",
        });
        localStorage.setItem("user", JSON.stringify(data));
      } catch (error) {
        setDetailsError(error.message || "Failed to load profile.");
      } finally {
        setPageLoading(false);
      }
    };

    loadProfile();
  }, []);

  const initials = getInitials(profile.full_name, profile.email);
  const avatarSrc = absoluteAvatarUrl(profile.avatar_url);
  const isDirty =
    draft.full_name.trim() !== (profile.full_name || "") ||
    draft.phone_number.trim() !== (profile.phone_number || "");

  const syncUser = (nextProfile) => {
    setProfile(nextProfile);
    setDraft({
      full_name: nextProfile.full_name || "",
      phone_number: nextProfile.phone_number || "",
    });
    localStorage.setItem("user", JSON.stringify(nextProfile));
  };

  const authHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
  });

  const handleDetailsSave = async (event) => {
    event.preventDefault();
    setDetailsError("");
    setDetailsSuccess("");

    const fullName = draft.full_name.trim();
    const phoneNumber = draft.phone_number.trim();

    if (fullName.length < 2) {
      setDetailsError("Full name must be at least 2 characters.");
      return;
    }
    if (phoneNumber && !/^[+\d\s()-]{7,20}$/.test(phoneNumber)) {
      setDetailsError("Enter a valid phone number.");
      return;
    }

    setSavingDetails(true);
    try {
      const response = await fetch(`${API}/auth/profile`, {
        method: "PUT",
        headers: {
          ...authHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          full_name: fullName,
          phone_number: phoneNumber || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Could not save profile details.");
      }

      syncUser(data);
      setDetailsSuccess("Profile details updated successfully.");
    } catch (error) {
      setDetailsError(error.message || "Could not save profile details.");
    } finally {
      setSavingDetails(false);
    }
  };

  const handleAvatarClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleAvatarChange = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    setDetailsError("");
    setDetailsSuccess("");

    if (!file) {
      return;
    }
    if (!file.type.startsWith("image/")) {
      setDetailsError("Please choose an image file.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setDetailsError("Image size should be below 5MB.");
      return;
    }

    setUploadingAvatar(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API}/auth/avatar`, {
        method: "POST",
        headers: authHeaders(),
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Could not upload avatar.");
      }

      syncUser(data);
      setDetailsSuccess("Profile photo updated successfully.");
    } catch (error) {
      setDetailsError(error.message || "Could not upload avatar.");
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleCancel = () => {
    setDraft({
      full_name: profile.full_name || "",
      phone_number: profile.phone_number || "",
    });
    setDetailsError("");
    setDetailsSuccess("");
  };

  const handlePasswordSubmit = async (form) => {
    setPasswordError("");
    setPasswordSuccess("");

    if (!form.current_password || !form.new_password || !form.confirm_password) {
      setPasswordError("All password fields are required.");
      return;
    }
    if (form.new_password.length < 6) {
      setPasswordError("New password must be at least 6 characters.");
      return;
    }
    if (form.new_password !== form.confirm_password) {
      setPasswordError("New password and confirm password must match.");
      return;
    }
    if (form.current_password === form.new_password) {
      setPasswordError("New password must be different from current password.");
      return;
    }

    setPasswordLoading(true);
    try {
      const response = await fetch(`${API}/auth/change-password`, {
        method: "POST",
        headers: {
          ...authHeaders(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current_password: form.current_password,
          new_password: form.new_password,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Could not change password.");
      }
      setPasswordSuccess(data.message || "Password updated successfully.");
    } catch (error) {
      setPasswordError(error.message || "Could not change password.");
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <>
      <div
        style={{
          maxWidth: 1040,
          margin: "0 auto",
          padding: "42px 24px 88px",
          display: "grid",
          gap: 24,
        }}
      >
        <section
          style={{
            ...cardStyle,
            padding: "30px clamp(20px, 4vw, 36px)",
            display: "grid",
            gap: 28,
          }}
        >
          <div>
            <button
              type="button"
              onClick={() => navigate("/dashboard")}
              style={{
                ...secondaryButtonStyle,
                padding: "10px 16px",
              }}
            >
              Back
            </button>
          </div>

          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 24,
              alignItems: "center",
            }}
          >
            <div style={{ position: "relative" }}>
              <p
                style={{
                  margin: "0 0 10px",
                  textAlign: "center",
                  color: "#15803d",
                  fontSize: "0.86rem",
                  fontWeight: 800,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                }}
              >
                Profile
              </p>
              <button
                type="button"
                onClick={handleAvatarClick}
                disabled={uploadingAvatar}
                style={{
                  width: 120,
                  height: 120,
                  borderRadius: "50%",
                  border: "4px solid rgba(21, 128, 61, 0.18)",
                  background: avatarSrc
                    ? `center / cover no-repeat url(${avatarSrc})`
                    : "linear-gradient(135deg, #15803d, #f59e0b)",
                  color: "#fff",
                  fontSize: "2rem",
                  fontWeight: 800,
                  display: "grid",
                  placeItems: "center",
                  cursor: uploadingAvatar ? "progress" : "pointer",
                  boxShadow: "0 18px 45px rgba(21, 128, 61, 0.2)",
                }}
              >
                {avatarSrc ? "" : initials}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={handleAvatarChange}
                style={{ display: "none" }}
              />
            </div>

            <div style={{ flex: "1 1 280px" }}>
              <h2 style={{ margin: 0, color: "#1c1917", fontSize: "1.4rem" }}>
                {profile.full_name || "Your profile"}
              </h2>
              <p style={{ margin: "8px 0 6px", color: "#57534e" }}>
                Click the avatar circle to upload a new profile photo.
              </p>
            </div>
          </div>

          {pageLoading ? <Message>Loading profile...</Message> : null}
          {detailsError ? <Message tone="error">{detailsError}</Message> : null}
          {detailsSuccess ? <Message tone="success">{detailsSuccess}</Message> : null}

          <form onSubmit={handleDetailsSave} style={{ display: "grid", gap: 18 }}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                gap: 18,
              }}
            >
              <Field label="Full Name">
                <input
                  type="text"
                  value={draft.full_name}
                  onChange={(event) => setDraft((current) => ({ ...current, full_name: event.target.value }))}
                  style={inputStyle}
                  placeholder="Enter your full name"
                />
              </Field>

              <Field label="Phone Number">
                <input
                  type="tel"
                  value={draft.phone_number}
                  onChange={(event) => setDraft((current) => ({ ...current, phone_number: event.target.value }))}
                  style={inputStyle}
                  placeholder="Enter your phone number"
                />
              </Field>
            </div>

            <Field label="Email Address" note="Email is read-only and cannot be changed.">
              <input type="email" value={profile.email || ""} style={{ ...inputStyle, color: "#78716c", background: "#f5f5f4" }} readOnly />
            </Field>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, flexWrap: "wrap" }}>
              <button type="button" onClick={handleCancel} disabled={!isDirty || savingDetails} style={secondaryButtonStyle}>
                Cancel
              </button>
              <button type="submit" disabled={savingDetails || uploadingAvatar || pageLoading} style={primaryButtonStyle}>
                {savingDetails ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </form>
        </section>
      </div>

      <PasswordModal
        open={passwordModalOpen}
        onClose={() => {
          setPasswordModalOpen(false);
          setPasswordError("");
          setPasswordSuccess("");
        }}
        onSubmit={handlePasswordSubmit}
        loading={passwordLoading}
        errorMessage={passwordError}
        successMessage={passwordSuccess}
      />
    </>
  );
}

const inputStyle = {
  width: "100%",
  padding: "13px 14px",
  borderRadius: 14,
  border: "1px solid rgba(120, 113, 108, 0.22)",
  background: "#ffffff",
  color: "#1c1917",
  fontSize: "0.96rem",
  outline: "none",
  boxSizing: "border-box",
};

const primaryButtonStyle = {
  border: "none",
  borderRadius: 14,
  padding: "12px 18px",
  background: "linear-gradient(135deg, #15803d, #166534)",
  color: "#fff",
  fontWeight: 700,
  cursor: "pointer",
  boxShadow: "0 16px 34px rgba(21, 128, 61, 0.2)",
};

const secondaryButtonStyle = {
  border: "1px solid rgba(120, 113, 108, 0.22)",
  borderRadius: 14,
  padding: "12px 18px",
  background: "#fff",
  color: "#292524",
  fontWeight: 700,
  cursor: "pointer",
};
