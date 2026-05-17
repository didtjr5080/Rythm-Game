# Local Development (Windows PowerShell)

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

## Gameplay Test Flow

1. Run backend
2. Run frontend
3. Open the web app
4. Upload audio
5. Click Analyze
6. Click Generate Notes
7. Click Play Game
8. Click Start
9. Play with D/F/J/K
