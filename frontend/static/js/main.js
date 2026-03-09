const html = document.documentElement;

const DEFAULT_THEME = 'dark';
const THEME_KEY = 'theme';

function initTheme() {
    const saved = localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
    if (saved === 'light') {
        html.classList.remove('dark');
    } else {
        html.classList.add('dark');
    }
}

function toggleTheme() {
    const isDark = html.classList.contains('dark');
    if (isDark) {
        html.classList.remove('dark');
        localStorage.setItem(THEME_KEY, 'light');
    } else {
        html.classList.add('dark');
        localStorage.setItem(THEME_KEY, 'dark');
    }
}

function initNav() {
    const toggle = document.getElementById('mobileNavToggle');
    const links = document.getElementById('navLinks');
    if (toggle && links) {
        toggle.addEventListener('click', () => links.classList.toggle('open'));
    }

    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
}

function showToast(message, type = 'info', timeout = 3200) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const iconMap = {
        info: 'fa-circle-info',
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        warning: 'fa-triangle-exclamation'
    };

    const item = document.createElement('div');
    item.className = `toast-item ${type}`;
    item.innerHTML = `
        <i class="fa-solid ${iconMap[type] || iconMap.info}"></i>
        <span>${message}</span>
    `;

    container.appendChild(item);
    window.setTimeout(() => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(8px)';
        window.setTimeout(() => item.remove(), 220);
    }, timeout);
}

function showLoading(button, label = 'Processing...') {
    if (!button) return;
    if (!button.dataset.originalHtml) {
        button.dataset.originalHtml = button.innerHTML;
    }
    button.disabled = true;
    button.innerHTML = `<span class="inline-flex items-center gap-2"><span class="spinner-ring" style="width:1rem;height:1rem;border-width:2px"></span>${label}</span>`;
}

function hideLoading(button) {
    if (!button) return;
    button.disabled = false;
    button.innerHTML = button.dataset.originalHtml || button.innerHTML;
}

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return String(meta?.content || '').trim();
}

function apiFetch(url, options = {}) {
    const merged = { credentials: 'same-origin', ...options };
    const method = String(merged.method || 'GET').toUpperCase();
    const headers = new Headers(merged.headers || {});

    if (!headers.has('Accept')) {
        headers.set('Accept', 'application/json');
    }

    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        const csrfToken = getCsrfToken();
        if (csrfToken && !headers.has('X-CSRF-Token')) {
            headers.set('X-CSRF-Token', csrfToken);
        }
    }

    merged.headers = headers;
    return fetch(url, merged);
}

async function refreshSavedRecipeCount() {
    const badge = document.getElementById('navSavedCountBadge');
    if (!badge) return;

    try {
        const response = await apiFetch('/api/dashboard/stats');
        const payload = await response.json();
        if (!response.ok || !payload.success) return;

        const data = (payload && payload.data && typeof payload.data === 'object')
            ? payload.data
            : payload;
        const stats = data.stats || payload.stats || {};
        const count = Number(stats.saved_count || 0);

        badge.textContent = String(count);
        badge.classList.toggle('hidden', count <= 0);

        const dashboardSaved = document.getElementById('statSavedRecipes');
        if (dashboardSaved) {
            dashboardSaved.textContent = String(count);
        }
    } catch (error) {
        // Best effort only.
    }
}

const NON_VEG_TERMS = new Set(['chicken', 'mutton', 'fish', 'egg', 'shrimp', 'pork', 'beef', 'bacon', 'turkey']);

function normalizeText(value) {
    return String(value || '')
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function detectRecipeType(recipe) {
    const explicit = String(recipe?.recipe_type || '').toLowerCase();
    if (explicit === 'veg' || explicit === 'non-veg') return explicit;

    const ingredients = Array.isArray(recipe?.normalized_ingredients)
        ? recipe.normalized_ingredients
        : (Array.isArray(recipe?.ingredients) ? recipe.ingredients : String(recipe?.ingredients || '').split(/,|\n/));

    const hasNonVeg = ingredients.some((item) => {
        const text = normalizeText(item);
        return Array.from(NON_VEG_TERMS).some((term) => new RegExp(`\\b${term}\\b`, 'i').test(text));
    });

    return hasNonVeg ? 'non-veg' : 'veg';
}

function getFallbackRecipeImage(recipe) {
    const recipeType = detectRecipeType(recipe);
    return recipeType === 'non-veg'
        ? '/static/images/recipe_placeholder_nonveg.svg'
        : '/static/images/recipe_placeholder_veg.svg';
}

function getRecipeImageUrl(recipe) {
    const explicit = String(recipe?.image_url || '').trim();
    if (explicit) return explicit;
    return getFallbackRecipeImage(recipe);
}

function withRecipeImageFallback(event) {
    const img = event?.target;
    if (!img) return;
    img.onerror = null;
    img.src = img.dataset.fallbackImage || '/static/images/recipe_placeholder_veg.svg';
}

function startPageTransition() {
    const root = document.getElementById('pageRoot');
    if (!root) return;
    root.classList.add('page-fade');
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initNav();
    startPageTransition();
    refreshSavedRecipeCount();
});

document.addEventListener('saved-recipes-updated', () => {
    refreshSavedRecipeCount();
});

window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.getRecipeImageUrl = getRecipeImageUrl;
window.getFallbackRecipeImage = getFallbackRecipeImage;
window.withRecipeImageFallback = withRecipeImageFallback;
window.detectRecipeType = detectRecipeType;
window.normalizeText = normalizeText;
window.getCsrfToken = getCsrfToken;
window.apiFetch = apiFetch;
window.refreshSavedRecipeCount = refreshSavedRecipeCount;
