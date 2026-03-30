# Ingredient-Based Intelligent Recipe Identification System

A comprehensive full-stack pipeline combining computer vision, OCR, and machine learning to identify raw ingredients from photos and extract ingredient text from product packets and recipe documents. This system integrates image preprocessing, CNN-based classification, robust OCR (Tesseract), an intelligent ML+OCR router, a FastAPI backend, and a ReactJS frontend.

## Highlights

- **End-to-end ingredient recognition**: From image upload to recipe suggestions
- **CNN-based classification**: Transfer learning with MobileNetV2 for 20+ ingredient classes
- **Advanced OCR**: Automatic preprocessing with Tesseract and intelligent PSM selection
- **Hybrid routing**: Smart ML vs. OCR decision engine based on image characteristics
- **RESTful API backend**: FastAPI with authentication and database support
- **Interactive frontend**: ReactJS + Vite with real-time results
- **Dataset utilities**: Scripts for downloading, augmenting, and validating ingredients
- **Visualization dashboard**: Per-input result cards and summary analytics

## Repository Structure

```
phase1_installation_testing/     # Environment setup & dependency testing
  ├── test_ocr.py                # Tesseract OCR validation
  └── test_opencv.py             # OpenCV functionality tests

phase2_image_handling/           # Image loading, resizing, and visualization
  ├── image_handling.py           # Core image I/O utilities
  ├── input_images/               # Sample test images
  └── output_images/              # Generated visualization outputs

phase3_preprocessing/            # Advanced image preprocessing pipeline
  ├── preprocess.py               # CLAHE, edge detection, thresholding
  ├── input_images/               # Test images before preprocessing
  └── preprocess_images/          # Preprocessed image cache

phase4_cnn_model/                # CNN training & model management
  ├── train_model.py              # MobileNetV2 transfer learning trainer
  ├── augment_dataset.py           # Data augmentation (rotation, zoom, etc.)
  ├── prepare_recipe_dataset.py   # Prepare recipe training data
  ├── fetch_wikipedia_images.py   # Auto-download ingredient images
  ├── ingredient_model.keras      # Trained ingredient classifier
  ├── class_names.json            # Ingredient class labels
  ├── dataset/                    # Training images by class
  ├── dataset_augmented/          # Augmented training set
  └── saved_model/                # Savedmodel checkpoint format

phase5_OCR/                      # Standalone OCR processing
  ├── ocr_with_filters.py         # Multi-preset PSM + preprocessing
  ├── input/                      # OCR test images
  └── output/                     # OCR results and logs

phase6_ML+OCR/                   # Hybrid ML + OCR router
  ├── main.py                     # Entry point for combined pipeline
  ├── ml_module.py                # ML inference wrapper
  ├── ocr_module.py               # OCR inference wrapper
  ├── ingredient.weights.h5       # Alternative model weights
  └── input/                      # Hybrid pipeline test images

phase7_backend/                  # FastAPI backend server
  ├── main.py                     # FastAPI app entry point
  ├── ml_module.py                # ML service integration
  ├── ocr_module.py               # OCR service integration
  ├── recipes_data.py             # Recipe database & utilities
  ├── requirements.txt            # Backend Python dependencies
  ├── check_db.py                 # Database integrity checker
  ├── create_sample_pdf.py        # Sample PDF generator
  ├── seed_real_data.py           # Database seeding script
  ├── app/                        # FastAPI route handlers
  ├── data/                       # Database files & schemas
  └── uploads/                    # User-uploaded image storage

frontend/                        # ReactJS + Vite frontend
  ├── src/
  │   ├── App.jsx                 # Main app component
  │   ├── main.jsx                # Entry point
  │   ├── pages/                  # Page components
  │   ├── components/             # Reusable UI components
  │   ├── context/                # React context (state management)
  │   └── utils/                  # Helper functions
  ├── public/
  │   ├── vegetables/             # Ingredient images
  │   └── project-images/         # UI assets
  ├── package.json                # NPM dependencies
  ├── vite.config.js              # Vite build config
  └── index.html                  # HTML template

dataset/                         # Primary ingredient dataset (~20 classes)
  ├── cabbage/, capsicum/, carrot/, cauliflower/
  ├── chicken/, cucumber/, egg/, eggplant/, fish/
  ├── garlic/, ginger/, lemon/, okra/, onion/
  ├── paneer/, peas/, potato/, rice/, spinach/, tomato/
  └── ... (additional ingredient folders)

dataset_recipe/                  # Recipe-augmented dataset
  └── (same structure as dataset/)

test/                            # Extended test dataset (40+ ingredient classes)
  └── apple/, banana/, beetroot/, bell pepper/, ... (comprehensive test set)

images/                          # Example placeholder & test images
  ├── tomato.svg
  ├── packet.svg
  └── dashboard.svg

Utility Scripts:
  ├── check_counts.py             # Verify dataset class distribution
  ├── check_dataset.py            # Dataset integrity validation
  └── download_images.py          # Batch download ingredients via web

TRAINING_GUIDE.md                # Detailed model training instructions
requirements.txt                 # Project-level dependencies (if any)
README.md                        # This file
```

## Quick Install

### 1. Prerequisites

Ensure Python 3.8+ is installed. Install system dependencies:

**Windows:**
```powershell
# Tesseract OCR (required for OCR pipeline)
# Download & install: https://github.com/UB-Mannheim/tesseract/wiki
# Default path: C:\Program Files\Tesseract-OCR\tesseract.exe

# Node.js (required for frontend)
# Download from: https://nodejs.org/
```

**macOS:**
```bash
brew install tesseract
brew install node
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install nodejs npm
```

### 2. Python Virtual Environment Setup

Navigate to the project root and create a virtual environment:

**PowerShell (Windows):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Bash (macOS/Linux):**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Backend Dependencies

```powershell
pip install -r phase7_backend/requirements.txt
```

### 4. Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

### 5. Configure Tesseract Path (OCR)

Update the Tesseract path in the OCR modules:

**phase5_OCR/ocr_with_filters.py** and **phase6_ML+OCR/ocr_module.py**:
```python
import pytesseract

# Windows example:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# macOS example:
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
```

### 6. Database & Data Preparation

```powershell
# Seed database with sample recipes (optional)
python phase7_backend/seed_real_data.py

# Verify database integrity
python phase7_backend/check_db.py
```

## Usage

### Phase 1: Testing & Verification

Verify your installation:

```bash
python phase1_installation_testing/test_opencv.py
python phase1_installation_testing/test_ocr.py
```

### Phase 2: Image Handling

Load, resize, and visualize images:

```bash
python phase2_image_handling/image_handling.py
```

### Phase 3: Image Preprocessing

Batch preprocess images (resize, CLAHE, edge detection, thresholding):

```bash
python phase3_preprocessing/preprocess.py
```

**Output:** Preprocessed images saved to `phase3_preprocessing/preprocess_images/`

### Phase 4: Model Training

**Train a new ingredient classifier:**

```bash
python phase4_cnn_model/train_model.py
```

**Augment training dataset:**

```bash
python phase4_cnn_model/augment_dataset.py
```

**Prepare recipe dataset:**

```bash
python phase4_cnn_model/prepare_recipe_dataset.py
```

**Fetch ingredient images from Wikipedia:**

```bash
python phase4_cnn_model/fetch_wikipedia_images.py
```

See [TRAINING_GUIDE.md](phase4_cnn_model/TRAINING_GUIDE.md) for detailed training instructions.

### Phase 5: OCR Pipeline

Extract text from ingredient packets or documents:

```bash
python phase5_OCR/ocr_with_filters.py
```

The script automatically tries multiple Tesseract preprocessing + PSM combinations for best results.

### Phase 6: ML + OCR Hybrid Router

Process images using intelligent ML vs. OCR routing:

```bash
python phase6_ML+OCR/main.py
```

The router analyzes image characteristics (text density, edge patterns) and selects the optimal pipeline.

### Phase 7: Backend API

Start the FastAPI server:

```powershell
# Make sure venv is activated
python phase7_backend/main.py
```

**Default:** http://localhost:8000

**API endpoints:**
- `POST /api/predict` — Classify ingredient from image
- `GET /api/recipes` — Fetch recipes by ingredient
- `POST /api/auth/login` — User authentication
- `GET /docs` — Interactive API documentation (Swagger UI)

### Frontend: React App

Start the development frontend:

```powershell
cd frontend
npm run dev
```

**Default:** http://localhost:5173

Build for production:

```powershell
npm run build
```

### Utility Scripts

**Check dataset class distribution:**

```bash
python check_counts.py
```

**Validate dataset integrity:**

```bash
python check_dataset.py
```

**Download ingredient images:**

```bash
python download_images.py
```

## Model Summary

### Architecture

- **Base Model:** MobileNetV2 (ImageNet pre-trained weights)
- **Custom Head:**
  - Global Average Pooling → BatchNormalization
  - Dense(128) → Dropout(0.4)
  - Dense(64) → Dropout(0.3)
  - Dense(20, softmax) — Output classes: 20 ingredient types

### Input Specifications

- **Input shape:** 224×224×3 (RGB images)
- **Preprocessing:** MobileNetV2 `preprocess_input()` (scales to [-1, 1])
  - ⚠️ **Important:** Never use simple `/255.0` scaling

### Training Configuration

- **Optimizer:** Adam (lr=0.001)
- **Loss:** Categorical Crossentropy
- **Data augmentation:** rotating, zooming, shifting, flipping
- **Batch size:** 32
- **Epochs:** 50 (with early stopping)

## Routing Logic

The hybrid router (Phase 6) intelligently selects between ML and OCR based on input image analysis:

1. **Image analysis:** Compute text-pixel ratio and edge density
2. **Decision threshold:** If text ratio > 15%, route to OCR; otherwise use ML
3. **ML path:** Image classification → ingredient + confidence score
4. **OCR path:** Multi-preset Tesseract → text extraction → recipe lookup
5. **Output:** Structured JSON with results, confidence, and recipe recommendations

## System Workflow

```
User Input (Image/PDF)
    ↓
[Phase 7 Backend] FastAPI Server
    ↓
[Phase 6 Router] ML vs. OCR Decision
    ├─→ [Phase 4 ML] Ingredient Classification
    │        ↓ (confidence + class label)
    │
    └─→ [Phase 5 OCR] Text Extraction
             ↓ (parsed ingredient list)
    ↓
[Database] Recipe Lookup
    ↓
[Frontend] Results Display
    ↓
User (Recipes + Suggestions)
```

## Troubleshooting & Tips

| Issue | Solution |
|-------|----------|
| **TesseractNotFoundError** | Verify tesseract_cmd path; reinstall Tesseract; ensure PATH environment variable is set |
| **Keras version mismatch** | Re-save models with matching local Keras version: `model.save('model.keras')` |
| **Wrong pixel scaling** | Always use `preprocess_input()` for MobileNetV2, never simple `/255.0` |
| **OCR returns empty** | Try higher resolution input (800×800+ px); ensure clean background; check Tesseract installation |
| **Model prediction too slow** | Use GPU acceleration (CUDA/cuDNN); or reduce input resolution to 224×224 |
| **Database connection error** | Check `phase7_backend/data/.env`; run `seed_real_data.py` to initialize DB |
| **Frontend cannot reach backend** | Ensure FastAPI server is running on port 8000; check CORS settings in `main.py` |
| **Module import errors** | Reactivate venv: `.\venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (macOS/Linux) |

## Examples

### Classify an ingredient image:

```bash
python phase6_ML+OCR/main.py
# Then upload: images/tomato.svg
```

### Extract text from a packet:

```bash
python phase5_OCR/ocr_with_filters.py
# Input: Product packet photo
# Output: Extracted ingredient list
```

### Start the full backend + frontend stack:

**Terminal 1 (Backend):**
```powershell
python phase7_backend/main.py
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

### Retrain model with custom dataset:

1. Organize images into `phase4_cnn_model/dataset/ClassName/` folders
2. Run `python phase4_cnn_model/train_model.py`
3. Model saved to `phase4_cnn_model/ingredient_model.keras`

## Contributing

Contributions are welcome! Suggested improvements:

- Add more ingredient classes (currently 20; expand to 50+)
- Improve OCR preprocessing heuristics (add morphological operations, edge enhancement)
- Integrate multi-language OCR support
- Add computer vision augmentation (brightness, contrast, saturation adjustment)
- Build mobile app using React Native
- Add real-time ingredient detection via webcam stream
- Improve recipe recommendation engine with user preferences
- Deploy backend to cloud (AWS Lambda, GCP Cloud Run, or Azure Functions)

Please open issues or PRs with proposed changes. Provide test cases for new features.

## Installation Checklist

- [ ] Python 3.8+ installed
- [ ] Tesseract OCR installed & path configured
- [ ] Node.js & npm installed
- [ ] Virtual environment created & activated
- [ ] Backend dependencies installed (`pip install -r phase7_backend/requirements.txt`)
- [ ] Frontend dependencies installed (`npm install` in `frontend/`)
- [ ] Database initialized (`python phase7_backend/seed_real_data.py`)
- [ ] Tesseract path set in OCR modules
- [ ] Tests passing (`test_opencv.py` and `test_ocr.py`)

## License & Author

Author: **VARA PRASAD**  
Organization: **Springboard Internship 2025** (Feb Batch 8)  
Branch: **varaprasad-project**  

**Team Contributors:**
- Image preprocessing & OCR optimization
- Model training & transfer learning
- Backend API development
- Frontend UI/UX design

---

**Last Updated:** March 2026

For questions or issues, please contact the development team or open a GitHub issue.
