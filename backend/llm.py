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

SYSTEM_PROMPT = """You are a helpful assistant that converts natural language questions
into SQLite SELECT queries.

Rules:
- Only output a single SQL SELECT statement. Nothing else.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or any other statement that changes data.
- Do not wrap the query in markdown code fences or add explanations.
- Only use the table and columns described in the schema below.
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
