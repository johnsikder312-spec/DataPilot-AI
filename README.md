# DataPilot AI

AI-powered Text-to-SQL app. Type a question in plain English, get the generated SQL and the results from a SQLite `students` database.

## Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI (Python)
- Database: SQLite
- LLM: Google Gemini (`google-generativeai`)

## Setup

### Backend
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Get a free key at https://aistudio.google.com/apikey, put it in `backend/.env` as `GEMINI_API_KEY=...`.

Run:
```
uvicorn main:app --reload
```

### Frontend
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## How it works

1. User types a question in the UI.
2. Frontend sends it to `POST /api/query` on the FastAPI backend.
3. Backend sends the question + database schema to Gemini, gets back SQL.
4. Backend validates the SQL is a safe, read-only `SELECT` (rejects `DROP`/`DELETE`/`UPDATE`/etc).
5. Backend runs it on SQLite, returns `{sql, columns, rows}`.
6. Frontend shows the generated SQL and a results table.

## Endpoints

- `GET /api/health` — liveness check.
- `POST /api/query` — `{"question": "..."}` → `{"sql", "columns", "rows"}`.
