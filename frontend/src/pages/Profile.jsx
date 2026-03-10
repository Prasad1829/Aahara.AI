export default function Profile() {
  const user = JSON.parse(localStorage.getItem("user"));
  const CARD = {
    background: "rgba(250,246,237,0.97)",
    borderRadius: 20,
    padding: 24,
    backdropFilter: "blur(8px)",
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "40px 24px 80px" }}>
      <div style={CARD}>
        <div style={{ height: 8 }} />
        <p style={{ color: "#6b7280", fontSize: "0.9rem", marginBottom: "16px" }}>
          Manage your account details and preferences.
        </p>
        <p style={{ margin: 0 }}>
          <strong>Email:</strong> {user?.email || "Not available"}
        </p>
      </div>
    </div>
  );
}
