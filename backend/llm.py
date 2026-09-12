"""
llm.py

Talks to the LLM API to turn a natural-language question into SQL.

Using Google Gemini (free tier available, no billing required for
normal testing volume). The API key is read from the GEMINI_API_KEY
environment variable (loaded from a local .env file by main.py) -
never hard-coded.
"""

import os
import re

import google.generativeai as genai

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

SYSTEM_PROMPT = """You convert natural language questions into SQL queries.

Database type: SQLite.
The only available table is "students". Its exact columns are given to you
below in the schema, on every request. That schema is the full extent of
the database - there are no other tables and no other columns.

Rules:
- Generate only SELECT queries. Never INSERT, UPDATE, DELETE, DROP, ALTER,
  or any statement that changes data.
- Never invent tables that aren't in the schema.
- Never invent columns that aren't in the schema.
- Return SQL only - no explanations, no comments, no markdown code fences
  (no ``` anywhere in your output).
- Output a single SQL statement, nothing else.
- If the question can't be answered with the given schema, return:
  SELECT 'Sorry, I cannot answer that question with the available data.' AS message;
"""


def _get_model() -> genai.GenerativeModel:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your key."
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)


def _clean_sql(text: str) -> str:
    """Strips markdown code fences and extra whitespace the model might add."""
    text = text.strip()
    text = re.sub(r"^```(sql)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text.rstrip(";").strip() + ";"


def generate_sql(question: str, schema_text: str) -> str:
    """Sends the question + schema to the LLM and returns a cleaned SQL string."""
    model = _get_model()

    user_prompt = f"""Database schema:
{schema_text}

Question: {question}

Write the single SQL SELECT query that answers this question."""

    response = model.generate_content(user_prompt)
    return _clean_sql(response.text)
