/**
 * api.ts
 *
 * Small helper for talking to the backend. Keeping fetch calls in one
 * place makes it easy to change the API URL or add error handling later.
 */

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface QueryResult {
  question: string;
  generated_sql: string;
  columns: string[];
  rows: unknown[][];
  row_count: number;
  execution_time: number;
  status: string;
}

export async function askQuestion(question: string): Promise<QueryResult> {
  const response = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong.");
  }

  return data as QueryResult;
}
