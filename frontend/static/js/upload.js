(function () {
    const dropZone = document.getElementById('uploadDropZone');
    const fileInput = document.getElementById('detectImage');
    const preview = document.getElementById('detectPreview');
    const detectBtn = document.getElementById('detectSubmitBtn');
    const ingredientsInput = document.getElementById('typedIngredients');
    const chipsHost = document.getElementById('detectedIngredientChips');
    const chipsSection = document.getElementById('detectedIngredientsSection');
    const openResultsBtn = document.getElementById('openResultsBtn');
    const loadingOverlay = document.getElementById('detectLoadingOverlay');
    const loadingStatus = document.getElementById('loadingStatusText');

    if (!detectBtn) return;

    const statusMessages = [
        'Detecting ingredients',
        'Finding recipes',
        'Fetching images'
    ];
    let statusTimer = null;
    let statusIdx = 0;

    function setStatus(text) {
        if (loadingStatus) loadingStatus.textContent = text;
    }

    function startLoader() {
        if (!loadingOverlay) return;
        loadingOverlay.classList.remove('hidden');
        statusIdx = 0;
        setStatus(statusMessages[statusIdx]);
        statusTimer = window.setInterval(() => {
            statusIdx = (statusIdx + 1) % statusMessages.length;
            setStatus(statusMessages[statusIdx]);
        }, 1300);
    }

    function stopLoader() {
        if (!loadingOverlay) return;
        loadingOverlay.classList.add('hidden');
        if (statusTimer) {
            window.clearInterval(statusTimer);
            statusTimer = null;
        }
    }

    function parseDetected(items) {
        const list = Array.isArray(items) ? items : [];
        const seen = new Set();
        const output = [];
        list.forEach((item) => {
            const key = window.normalizeText(item?.ingredient);
            if (!key || seen.has(key)) return;
            seen.add(key);
            output.push(item);
        });
        return output;
    }

    function renderDetectedChips(items) {
        if (!chipsHost || !chipsSection) return;
        chipsHost.innerHTML = '';
        const unique = parseDetected(items);
        if (!unique.length) {
            chipsSection.classList.add('hidden');
            return;
        }

        chipsSection.classList.remove('hidden');
        unique.forEach((item) => {
            const chip = document.createElement('span');
            chip.className = 'ingredient-chip';
            chip.textContent = item.ingredient;
            chipsHost.appendChild(chip);
        });
    }

    function bindDropzone() {
        if (!dropZone || !fileInput) return;

        ['dragenter', 'dragover'].forEach((eventName) => {
            dropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                dropZone.classList.add('drag-active');
            });
        });

        ['dragleave', 'drop'].forEach((eventName) => {
            dropZone.addEventListener(eventName, (event) => {
                event.preventDefault();
                dropZone.classList.remove('drag-active');
            });
        });

        dropZone.addEventListener('drop', (event) => {
            const files = event.dataTransfer?.files;
            if (!files || !files.length) return;
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        });

        dropZone.addEventListener('click', () => fileInput.click());
    }

    function bindPreview() {
        if (!fileInput || !preview) return;
        fileInput.addEventListener('change', () => {
            const file = fileInput.files?.[0];
            if (!file) {
                preview.classList.add('hidden');
                return;
            }
            if (!file.type.startsWith('image/')) {
                window.showToast('Please select a valid image file', 'error');
                fileInput.value = '';
                preview.classList.add('hidden');
                return;
            }
            if (file.size > 10 * 1024 * 1024) {
                window.showToast('Image should be less than 10MB', 'error');
                fileInput.value = '';
                preview.classList.add('hidden');
                return;
            }
            const reader = new FileReader();
            reader.onload = (event) => {
                preview.src = event.target.result;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        });
    }

    async function submitDetection() {
        const typed = String(ingredientsInput?.value || '').trim();
        const image = fileInput?.files?.[0] || null;

        if (!typed && !image) {
            window.showToast('Add ingredients or upload an image first', 'warning');
            return;
        }

        const formData = new FormData();
        if (typed) formData.append('ingredients', typed);
        if (image) formData.append('image', image);

        window.showLoading(detectBtn, 'Analyzing...');
        startLoader();
        const controller = new AbortController();
        let didTimeout = false;
        const timeoutHandle = window.setTimeout(() => {
            didTimeout = true;
            controller.abort();
        }, 90000);
        try {
            const response = await window.apiFetch('/api/detect', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            const payload = await response.json();

            if (response.status === 401) {
                window.location.href = '/login?next=/upload';
                return;
            }
            if (!response.ok || !payload.success) {
                throw new Error(payload.message || 'Detection failed');
            }

            localStorage.setItem('recipes', JSON.stringify(payload.recipes || []));
            localStorage.setItem('detected', JSON.stringify(payload.detected || []));
            localStorage.setItem('search_terms', JSON.stringify(payload.search_terms || []));
            localStorage.setItem('primary_ingredient', payload.ingredient || '');
            localStorage.setItem('recommendation_explanation', payload.explanation || '');

            renderDetectedChips(payload.detected || []);
            if (openResultsBtn) {
                openResultsBtn.classList.remove('hidden');
            }
            window.showToast(`Found ${(payload.recipes || []).length} recipe matches`, 'success');
        } catch (error) {
            if (didTimeout || error?.name === 'AbortError') {
                window.showToast('Detection timed out. Please try a smaller image or typed ingredients.', 'error');
            } else {
                window.showToast(error.message || 'Something went wrong', 'error');
            }
        } finally {
            window.clearTimeout(timeoutHandle);
            stopLoader();
            window.hideLoading(detectBtn);
        }
    }

    bindDropzone();
    bindPreview();

    detectBtn.addEventListener('click', submitDetection);
    if (openResultsBtn) {
        openResultsBtn.addEventListener('click', () => {
            window.location.href = '/recipe-results';
        });
    }
})();
