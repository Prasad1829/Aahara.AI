import { motion } from "framer-motion";

export default function DetectionResult({ detected_ingredients, detection }) {
  const detected = detected_ingredients || [];
  const status = detection?.status;
  const textFound = detection?.text_found;
  const message = detection?.message;

  return (
    <>
      <h2 className="mb-2 text-lg font-bold text-stone-900">Detected Ingredients</h2>

      {/* ── CASE 1: Food ingredients detected ── */}
      {detected.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {detected.map((ingredient, idx) => (
            <motion.span
              key={`${ingredient}-${idx}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: idx * 0.04 }}
              className="rounded-full border border-green-200 bg-green-50 px-3 py-1 text-sm text-green-700"
              style={{ willChange: "transform, opacity" }}
            >
              🥦 {ingredient}
            </motion.span>
          ))}
        </div>
      )}

      {/* ── CASE 2: Text found in image ── */}
      {(status === "text_only" || textFound) && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-3"
        >
          <p className="text-sm font-semibold text-blue-800">📝 Text Found in Image</p>
          <p className="mt-1 text-sm text-blue-700">{textFound}</p>
        </motion.div>
      )}

      {/* ── CASE 3: Not a food image ── */}
      {(status === "not_food" || status === "not_recognized") && detected.length === 0 && !textFound && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3"
        >
          <p className="text-sm font-semibold text-red-700">❌ Not a food ingredient</p>
          <p className="mt-1 text-sm text-red-600">Please upload a vegetable or food image.</p>
        </motion.div>
      )}

      {/* ── CASE 4: No detection at all ── */}
      {detected.length === 0 && !textFound && status !== "not_food" && status !== "not_recognized" && (
        <p className="text-stone-500 italic">No ingredients detected.</p>
      )}

      {/* ── SOURCE & CONFIDENCE ── only for food images ── */}
      {detection && detected.length > 0 && (
        <p className="mt-2 text-sm text-stone-600">
          Source: <span className="font-semibold">{detection.source || "n/a"}</span>, Confidence:{" "}
          <span className="font-semibold">{Math.round((detection.confidence || 0) * 100)}%</span>
        </p>
      )}

      {/* ── TOP PREDICTIONS ── only show for food images ── */}
      {detection?.top_predictions?.length > 0 &&
        status !== "text_only" &&
        status !== "not_food" &&
        status !== "not_recognized" && (
          <div className="mt-3 rounded-lg border border-stone-200 bg-stone-50 p-3">
            <p className="text-sm font-semibold text-stone-800">Top Predictions</p>
            <ul className="mt-1 space-y-1 text-sm text-stone-700">
              {detection.top_predictions.map((pred, idx) => (
                <li key={`${pred.ingredient}-${idx}`}>
                  {idx + 1}. {pred.ingredient} ({Math.round((pred.confidence || 0) * 100)}%)
                </li>
              ))}
            </ul>
            {(detection.confidence || 0) < 0.6 && detected.length === 0 && !textFound && (
              <p className="mt-2 text-xs text-amber-700">
                Prediction confidence is low. Use manual ingredient correction.
              </p>
            )}
          </div>
        )}
    </>
  );
}