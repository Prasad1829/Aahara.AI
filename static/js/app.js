const form = document.getElementById("genForm");

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const queryInput = document.getElementById("query");
    const loader = document.getElementById("loader");
    const out = document.getElementById("out");

    const q = queryInput.value.trim();
    if (!q) return;

    // Clear previous result
    out.innerHTML = "";
    loader.classList.remove("hidden");

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q })
      });

      const data = await response.json();
      loader.classList.add("hidden");

      if (!data.ok) {
        out.innerHTML = `
          <div class="result">
            <b>Error:</b> ${data.error}
          </div>
        `;
        return;
      }

      const modeLabel =
        data.mode === "generated"
          ? `<span class="badge">AI Generated</span>`
          : `<span class="badge">Matched</span>`;

      out.innerHTML = data.results.map(r => {

        const ingredientsHTML = r.ingredients
          .map(i => `<span class="badge">${i}</span>`)
          .join(" ");

        const matchedHTML = (r.matched || [])
          .map(i => `<span class="badge">${i}</span>`)
          .join(" ");

        const missingHTML = (r.missing || [])
          .map(i => `<span class="badge">${i}</span>`)
          .join(" ");

        const stepsHTML = (r.steps || [])
          .map(step => `<li>${step}</li>`)
          .join("");

        return `
          <div class="result">
            <div class="result-top">

              <!-- IMAGE WITH FALLBACK -->
              <img 
                src="/static/images/${r.image}" 
                alt="recipe"
                onerror="this.onerror=null; this.src='/static/images/food.jpg';"
              >

              <div>
                ${modeLabel}
                ${r.score ? `<span class="badge">${r.score}% match</span>` : ""}

                <h2 style="margin:8px 0 6px">${r.name}</h2>
                <div class="muted">
                  ${r.cuisine || ""} 
                  ${r.time ? " • " + r.time : ""} 
                  ${r.difficulty ? " • " + r.difficulty : ""}
                </div>

                <h3 style="margin:12px 0 8px">Ingredients</h3>
                <div>${ingredientsHTML}</div>

                <h3 style="margin:12px 0 8px">Matched</h3>
                <div>${matchedHTML || "<span class='muted'>None</span>"}</div>

                <h3 style="margin:12px 0 8px">Missing</h3>
                <div>${missingHTML || "<span class='muted'>None</span>"}</div>

                <!-- SAVE BUTTON -->
                <form method="POST" action="/save" style="margin-top:10px">
                  <input type="hidden" name="recipe_name" value="${r.name}">
                  <button class="btn" type="submit">Save Recipe</button>
                </form>

              </div>
            </div>

            <h3 style="margin:14px 0 8px">Steps</h3>
            <ol>${stepsHTML}</ol>
          </div>
        `;
      }).join("");

    } catch (error) {
      loader.classList.add("hidden");
      out.innerHTML = `
        <div class="result">
          <b>Server Error:</b> ${error}
        </div>
      `;
    }
  });
}
