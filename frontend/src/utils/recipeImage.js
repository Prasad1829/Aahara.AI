const PALETTES = [
  { bg: "#f2e5c3", accent: "#c8873a", text: "#6f4518" },
  { bg: "#dfead5", accent: "#4a9e6b", text: "#24513a" },
  { bg: "#eadcd2", accent: "#b56a4c", text: "#693521" },
  { bg: "#e1ddf3", accent: "#8a52c8", text: "#4f2a77" },
];

function hashText(value = "") {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
  }
  return hash;
}

function getInitials(name = "") {
  const parts = String(name || "Recipe").trim().split(/\s+/).filter(Boolean);
  const initials = parts.slice(0, 2).map((part) => part[0]?.toUpperCase() || "").join("");
  return initials || "R";
}

export function getRecipeImage(name = "") {
  const label = String(name || "Recipe");
  const palette = PALETTES[hashText(label) % PALETTES.length];
  const initials = getInitials(label);

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200" role="img" aria-label="${label}">
      <rect width="200" height="200" rx="28" fill="${palette.bg}" />
      <circle cx="100" cy="76" r="38" fill="${palette.accent}" opacity="0.18" />
      <rect x="28" y="126" width="144" height="16" rx="8" fill="${palette.accent}" opacity="0.18" />
      <rect x="48" y="152" width="104" height="12" rx="6" fill="${palette.accent}" opacity="0.12" />
      <text x="100" y="95" text-anchor="middle" font-size="34" font-family="DM Sans, Arial, sans-serif" font-weight="700" fill="${palette.text}">${initials}</text>
    </svg>
  `;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}
