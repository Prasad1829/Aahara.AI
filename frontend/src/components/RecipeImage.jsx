import { useEffect, useMemo, useState } from "react";
import { getRecipeImageSources } from "../utils/recipeImage";

export default function RecipeImage({ name = "", ingredients = [], alt, onError, ...props }) {
  const sources = useMemo(() => getRecipeImageSources(name, ingredients), [ingredients, name]);
  const [sourceIndex, setSourceIndex] = useState(0);

  useEffect(() => {
    setSourceIndex(0);
  }, [sources]);

  return (
    <img
      {...props}
      src={sources[Math.min(sourceIndex, sources.length - 1)]}
      alt={alt || name || "Recipe"}
      onError={(event) => {
        onError?.(event);
        setSourceIndex((current) => (
          current < sources.length - 1 ? current + 1 : current
        ));
      }}
    />
  );
}
