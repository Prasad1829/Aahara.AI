import { motion } from "framer-motion";

export default function DetectionResult({ detected_ingredients, detection }) {
  const detected = detected_ingredients || [];

  return (
    <>
      <h2 className="mb-2 text-lg font-bold text-stone-900">Detected Ingredients</h2>
      <div className="flex flex-wrap gap-2">
        {detected.length > 0 ? (
          detected.map((ingredient, idx) => (
            <motion.span
              key={`${ingredient}-${idx}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: idx * 0.04 }}
              className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-sm text-stone-700"
              style={{ willChange: "transform, opacity" }}
            >
              {ingredient}
            </motion.span>
          ))
        ) : (
          <p className="text-stone-700">No ingredients detected.</p>
        )}
      </div>

      {detection && (
        <p className="mt-2 text-sm text-stone-600">
          Source: <span className="font-semibold">{detection.source || "n/a"}</span>, Confidence:{" "}
          <span className="font-semibold">{Math.round((detection.confidence || 0) * 100)}%</span>
        </p>
      )}

      {detection?.top_predictions?.length > 0 && (
        <div className="mt-3 rounded-lg border border-stone-200 bg-stone-50 p-3">
          <p className="text-sm font-semibold text-stone-800">Top Predictions</p>
          <ul className="mt-1 space-y-1 text-sm text-stone-700">
            {detection.top_predictions.map((pred, idx) => (
              <li key={`${pred.ingredient}-${idx}`}>
                {idx + 1}. {pred.ingredient} ({Math.round((pred.confidence || 0) * 100)}%)
              </li>
            ))}
          </ul>
          {(detection.confidence || 0) < 0.6 && (
            <p className="mt-2 text-xs text-amber-700">
              Prediction confidence is low. Use manual ingredient correction.
            </p>
          )}
        </div>
      )}
    </>
  );
}
