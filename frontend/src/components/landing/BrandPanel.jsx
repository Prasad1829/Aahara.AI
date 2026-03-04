import { Camera, ChefHat, Leaf, UtensilsCrossed } from "lucide-react";

export default function BrandPanel({ onStart }) {
  return (
    <div
      className="w-full max-w-[435px] rounded-[22px] border border-[#ece7dc] px-8 py-9 md:px-10 md:py-10"
      style={{
        backdropFilter: "blur(20px)",
        background: "#FFF8E7",
        boxShadow:
          "0 25px 50px -12px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.1) inset, 0 -1px 0 0 rgba(0,0,0,0.05) inset",
      }}
    >
      {/* ── Top decorative row ── */}
      <div className="mb-10 flex items-center justify-center gap-3">
        <Leaf size={18} className="text-emerald-700" aria-hidden="true" />
        <div className="h-px w-16 bg-gradient-to-r from-transparent via-green-700 to-transparent" />
        <UtensilsCrossed size={18} className="text-emerald-700" aria-hidden="true" />
        <div className="h-px w-16 bg-gradient-to-r from-transparent via-green-700 to-transparent" />
        <Leaf size={18} className="text-emerald-700" aria-hidden="true" />
      </div>

      {/* ── Title with chef hat ~10mm above I ── */}
      <h1
        className="relative text-center text-4xl font-bold leading-none md:text-5xl cursor-default select-none"
        style={{ fontFamily: '"Playfair Display", Georgia, serif', color: "#C7772C" }}
      >
        Aahara.A
        <span className="relative inline-block">
          I
          <ChefHat
            className="pointer-events-none absolute left-1/2 -top-11 h-11 w-11 -translate-x-1/2 md:-top-12 md:h-13 md:w-13"
            style={{ fill: "#ffffff", stroke: "#111111", strokeWidth: 2.4 }}
            aria-hidden="true"
          />
        </span>
      </h1>

      {/* ── Subtitle ── */}
      <p className="mx-auto mt-3 max-w-[396px] text-center text-[14px] font-light text-gray-600 md:text-[19px] cursor-default select-none">
        Personalized Nutrition at Your Fingertips
      </p>

      {/* ── Divider ── */}
      <div className="my-6 flex justify-center">
        <div className="h-0.5 w-24 rounded-full bg-gradient-to-r from-transparent via-green-700 to-transparent" />
      </div>

      {/* ── Scan & Cook icons ── */}
      <div className="mb-8 flex justify-center gap-10">
        <div className="text-center">
          <div className="mx-auto mb-2 flex h-13 w-13 items-center justify-center rounded-full bg-gradient-to-br from-green-100 to-green-200 shadow">
            <Camera size={19} className="text-green-800" />
          </div>
          <span className="text-base font-medium text-gray-600 md:text-[19px] cursor-default select-none">Scan</span>
        </div>
        <div className="text-center">
          <div className="mx-auto mb-2 flex h-13 w-13 items-center justify-center rounded-full bg-gradient-to-br from-amber-100 to-amber-200 shadow">
            <ChefHat size={19} className="text-amber-800" />
          </div>
          <span className="text-base font-medium text-gray-600 md:text-[19px] cursor-default select-none">Cook</span>
        </div>
      </div>

      {/* ── Lets Go button ── */}
      <div className="mt-5 flex justify-center">
        <div className="relative inline-flex">
          <button
            onClick={onStart}
            className="group relative rounded-full bg-[#7BAF83] px-10 py-3 text-base font-semibold text-white shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl md:text-[26px]"
          >
            <span className="relative z-10 inline-flex items-center">Lets Go</span>
            <span className="absolute inset-0 rounded-full bg-[#6CA274] opacity-0 transition-opacity group-hover:opacity-100" />
          </button>
        </div>
      </div>
    </div>
  );
}