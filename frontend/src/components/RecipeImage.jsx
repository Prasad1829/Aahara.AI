import { useEffect, useMemo, useState } from "react";
import { getRecipeImageSources } from "../utils/recipeImage";

export default function RecipeImage({
  name = "",
  ingredients = [],
  imageUrl,
  imageFallbackUrl,
  alt,
  onError,
  ...props
}) {
  const ingredientKey = Array.isArray(ingredients)
    ? ingredients.filter(Boolean).join("|")
    : String(ingredients || "");

  const sources = useMemo(() => {
    const generatedSources = getRecipeImageSources(name, ingredients);
    return [...new Set([imageUrl, imageFallbackUrl, ...generatedSources].filter(Boolean))];
  }, [imageFallbackUrl, imageUrl, ingredientKey, name]);

  const sourceKey = useMemo(() => sources.join("|"), [sources]);
  const [sourceIndex, setSourceIndex] = useState(0);

  useEffect(() => {
    setSourceIndex(0);
  }, [sourceKey]);

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
