import { useEffect, useState } from "react";

const SLIDES = [
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80",
  "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=1920&q=80",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=1920&q=80",
  "https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=1920&q=80",
  "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=1920&q=80",
  "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=1920&q=80",
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1920&q=80",
  "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1920&q=80",
];

export default function SlideshowBackground() {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % SLIDES.length);
    }, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <>
      <div className="absolute inset-0 overflow-hidden bg-black">
        {SLIDES.map((url, index) => (
          <div
            key={url}
            className={`absolute inset-0 bg-cover bg-center transition-opacity duration-[1500ms] ease-in-out ${
              activeIndex === index ? "opacity-100" : "opacity-0"
            }`}
            style={{
              backgroundImage: `linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.4)), url('${url}')`,
            }}
          />
        ))}
      </div>
    </>
  );
}
