import Navbar from "./Navbar";

const DEFAULT_BG = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80";

export default function AppLayout({ children, user, bgImage }) {
  const background = bgImage || DEFAULT_BG;

  return (
    <div className="app-layout">
      <div
        className="app-background"
        style={{
          backgroundImage: `linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.6)), url('${background}')`,
        }}
      />
      <div className="app-foreground">
        <Navbar user={user} />
        <main className="app-content">
          {children}
        </main>
        <footer className="footer">
          © 2026 Aahara.AI · Developed by Vara Prasad · Email: varaprasad42c4@gmail.com · Visakhapatnam
        </footer>
      </div>
    </div>
  );
}
