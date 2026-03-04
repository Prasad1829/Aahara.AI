# Indian Ingredient Model Training Guide

## 1. Dataset structure
Create folder-per-class under `p:\INFOSYS PROJECT\dataset`.

Example:

```text
dataset/
  onion/
    img1.jpg
    img2.jpg
  tomato/
  potato/
  chicken/
  fish/
  paneer/
  ...
```

Notes:
- Keep at least 150 to 300 images per class for useful results.
- Use the same naming format as ingredient labels you want in backend.

## 2. Train model
From project root:

```powershell
cd "p:\INFOSYS PROJECT"
python phase4_cnn_model\train_model.py --dataset-dir "p:\INFOSYS PROJECT\dataset" --epochs 12 --batch-size 32
```

This creates:
- `phase4_cnn_model/ingredient_model.keras`
- `phase4_cnn_model/class_names.json`

## 3. Restart backend

```powershell
cd "p:\INFOSYS PROJECT\phase7_backend"
uvicorn main:app --reload
```

Backend `ml_service.py` auto-loads `class_names.json` so your trained classes are used without code edits.

## 4. Recommended initial Indian classes

- onion, tomato, potato, carrot, cucumber, cabbage, cauliflower, capsicum
- eggplant, okra, peas, spinach, methi, drumstick
- ginger, garlic, lemon
- paneer, yogurt, butter
- rice, atta, maida, semolina
- toor dal, moong dal, chana dal, masoor dal, rajma, chickpeas
- egg, chicken, fish, mutton
- chili, turmeric, cumin, coriander powder, garam masala
