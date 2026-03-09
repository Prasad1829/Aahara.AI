# Ingredient Recipe AI Quickstart

## 1) Open backend

```powershell
cd "C:\Users\ASUS\Desktop\Infosys virtual internship\Project\ingredient_recipe_ai\backend"
```

## 2) Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 3) Configure environment

Create `ingredient_recipe_ai/.env` from `.env.example` and set at least:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

## 4) Apply migrations

```powershell
flask --app run.py db upgrade
```

## 5) Start app

```powershell
python run.py
```

Open:
- `http://localhost:5000`

## 6) Basic flow

1. Register
2. Login
3. Upload image or type ingredients
4. Open recipe results
5. Save/Unsave recipes
6. View dashboard and saved pages
7. Open `/admin` with admin account

## 7) Run tests + coverage

```powershell
pytest -q tests
pytest --cov=app tests/
```
