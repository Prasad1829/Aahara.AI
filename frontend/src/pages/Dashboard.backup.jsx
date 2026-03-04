<section className="mt-5 overflow-hidden rounded-3xl p-[2px]"
  style={{
    background: "linear-gradient(135deg, #2d6a4f, #52b788, #1b4332)",
  }}
>
  <div className="rounded-3xl overflow-hidden"
    style={{
      background: "linear-gradient(145deg, #0a1628 0%, #0d2137 50%, #0a1628 100%)",
    }}
  >
    <div className="flex flex-col items-stretch gap-0 md:flex-row">

      {/* ── LEFT: Info Panel ── */}
      <div className="relative z-10 flex flex-col justify-center p-8 md:w-1/2 md:p-10">

        {/* Badge */}
        <div className="mb-6 inline-flex w-fit items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-widest text-emerald-400">
            Select Vegetables
          </span>
        </div>

        {/* Title */}
        <h2
          className="text-5xl font-black leading-none tracking-tight text-white md:text-6xl"
          style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
        >
          AHARA
          <span className="block text-transparent"
            style={{
              WebkitTextStroke: "2px #52b788",
            }}
          >
            AI
          </span>
        </h2>

        {/* Divider */}
        <div className="my-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-gradient-to-r from-emerald-500/50 to-transparent" />
          <div className="h-1 w-1 rounded-full bg-emerald-400" />
        </div>

        {/* Description */}
        <p className="max-w-xs text-sm leading-relaxed text-slate-400 md:text-base">
          Rotate the track and tap any vegetable to select it. Build your ingredient list instantly.
        </p>

        {/* Use Selected Button */}
        <button
          onClick={applySelectedVeggies}
          className="mt-8 w-fit rounded-2xl px-7 py-3.5 text-sm font-bold tracking-wide transition-all duration-300"
          style={{
            background: selectedVeggies.length > 0
              ? "linear-gradient(135deg, #52b788, #2d6a4f)"
              : "rgba(255,255,255,0.05)",
            color: selectedVeggies.length > 0 ? "#fff" : "#64748b",
            border: selectedVeggies.length > 0
              ? "1px solid #52b788"
              : "1px solid rgba(255,255,255,0.1)",
            boxShadow: selectedVeggies.length > 0
              ? "0 8px 32px rgba(82,183,136,0.3)"
              : "none",
          }}
        >
          {selectedVeggies.length > 0
            ? `✓ Use ${selectedVeggies.length} Selected`
            : "Tap a vegetable first"}
        </button>

        {/* Selected Veggie Tags */}
        {selectedVeggies.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {selectedVeggies.map((v) => (
              <span
                key={v}
                className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-medium capitalize text-emerald-300"
              >
                {v}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* ── RIGHT: Circular Slider ── */}
      <div className="relative flex flex-col items-center justify-center p-6 md:w-1/2 md:p-8">

        {/* Glow effect behind slider */}
        <div
          className="absolute inset-0 opacity-20"
          style={{
            background: "radial-gradient(circle at center, #52b788 0%, transparent 70%)",
          }}
        />

        <CircularSlider
          items={vegetableOptions}
          selectedItems={selectedVeggies}
          onToggleItem={toggleVeggie}
        />

        <p className="mt-4 text-xs font-medium tracking-widest text-slate-500 uppercase">
          {selectedVeggies.length > 0
            ? `${selectedVeggies.length} vegetable${selectedVeggies.length > 1 ? "s" : ""} selected`
            : "Tap a vegetable to select"}
        </p>
      </div>

    </div>
  </div>
</section>