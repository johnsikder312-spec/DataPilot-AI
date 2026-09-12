"""
main.py

The FastAPI application. Defines two endpoints:

  GET  /api/health   -> simple check that the server is alive
  POST /api/query    -> the main flow:
                         question -> LLM -> SQL -> validate -> run -> results

Run with:  uvicorn main:app --reload
"""

import re
import time

from dotenv import load_dotenv

load_dotenv()  # reads backend/.env into environment variables

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database
import llm

app = FastAPI(title="DataPilot AI")

# Allow the local Vite dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()


class QueryRequest(BaseModel):
    question: str


# Words that must never appear in a query we're about to run.
# We only ever want to run read-only SELECT statements.
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "TRUNCATE", "CREATE", "REPLACE", "ATTACH", "PRAGMA",
]

SAFETY_ERROR = "This query is not allowed. Only read-only SELECT queries are supported."


def validate_select_query(sql: str) -> None:
    """Raises ValueError if the SQL is not a safe, single SELECT statement."""
    cleaned = sql.strip().rstrip(";").strip()

    if not re.match(r"^SELECT\b", cleaned, re.IGNORECASE):
        raise ValueError(SAFETY_ERROR)

    if ";" in cleaned:
        raise ValueError(SAFETY_ERROR)

    upper_sql = cleaned.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            raise ValueError(SAFETY_ERROR)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/query")
def query(request: QueryRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    schema_text = database.get_schema_text()

    try:
        sql = llm.generate_sql(question, schema_text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {e}")

    try:
        validate_select_query(sql)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    start = time.perf_counter()
    try:
        columns, rows = database.run_select_query(sql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to run SQL: {e}")
    execution_time = round(time.perf_counter() - start, 4)

    return {
        "question": question,
        "generated_sql": sql,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "execution_time": execution_time,
        "status": "success",
    }
