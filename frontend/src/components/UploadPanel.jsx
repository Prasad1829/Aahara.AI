import { useRef, useState } from "react";
import { motion } from "framer-motion";
import LoadingButton from "./LoadingButton";

function AIProcessingIndicator() {
  return (
    <div className="mt-3 rounded-xl border border-blue-200/70 bg-blue-50/70 p-3">
      <div className="flex items-center gap-3">
        <span className="spinner border-blue-300 border-t-blue-600" />
        <div>
          <p className="text-sm font-semibold text-blue-900">AI is processing images</p>
          <p className="text-xs text-blue-700">Detecting ingredients and ranking recipes...</p>
        </div>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-blue-100">
        <motion.div
          className="h-full w-1/3 bg-gradient-to-r from-transparent via-blue-400/70 to-transparent"
          initial={{ x: "-120%" }}
          animate={{ x: "350%" }}
          transition={{ duration: 1.3, ease: "linear", repeat: Infinity }}
          style={{ willChange: "transform" }}
        />
      </div>
    </div>
  );
}

export default function UploadPanel({ files, setFiles, onUpload, loading }) {
  const fileInputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const addFiles = (incoming) => {
    const arr = Array.from(incoming || []);
    if (arr.length === 0) return;

    setFiles((prev) => {
      const deduped = arr.filter(
        (candidate) =>
          !prev.some((existing) => existing.name === candidate.name && existing.size === candidate.size)
      );
      return [...prev, ...deduped];
    });
  };

  const removeFile = (name) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  };

  return (
    <>
      <input
        type="file"
        accept="image/*"
        multiple
        ref={fileInputRef}
        onChange={(e) => addFiles(e.target.files)}
        className="hidden"
      />

      <section className="relative overflow-hidden rounded-2xl border border-white/60 bg-white/45 p-4 md:p-5 backdrop-blur-lg">
        <div className={loading ? "loading-shimmer" : ""} />
        <p className="text-sm font-semibold text-slate-800">Drag and drop multiple images here</p>
        <p className="mt-1 text-xs text-slate-600">or click Select Images to choose files</p>

        <div className="mt-3 flex flex-col gap-3 sm:flex-row">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="motion-btn min-h-11 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            Select Images
          </button>

          <LoadingButton
            onClick={onUpload}
            loading={loading}
            label="Generate Recipe"
            loadingLabel="Analyzing..."
            className="bg-cyan-600 text-white hover:bg-cyan-700"
          />
        </div>

        {loading && <AIProcessingIndicator />}

        <div
          className={`mt-3 rounded-xl border-2 border-dashed p-3 text-xs text-slate-600 transition ${
            dragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 bg-white/50"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragActive(false);
            addFiles(e.dataTransfer.files);
          }}
        >
          Drop images here
        </div>
      </section>

      {files.length > 0 && (
        <motion.div layout transition={{ duration: 0.22 }} className="mt-4 rounded-xl border border-stone-200 bg-white p-4">
          <p className="mb-2 text-sm font-semibold text-stone-800">Selected Files ({files.length})</p>
          <div className="flex flex-wrap gap-2">
            {files.map((f) => (
              <div
                key={`${f.name}-${f.size}`}
                className="inline-flex min-h-10 items-center gap-2 rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm"
              >
                <span className="text-slate-700">{f.name}</span>
                <button
                  className="min-h-8 min-w-8 font-bold text-rose-600"
                  onClick={() => removeFile(f.name)}
                  aria-label={`Remove ${f.name}`}
                >
                  x
                </button>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </>
  );
}
