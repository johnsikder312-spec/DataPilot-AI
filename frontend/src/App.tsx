import { useState } from "react";
import { askQuestion, QueryResult } from "./api";

const EXAMPLE_QUESTIONS = [
  "Show all students.",
  "Show students who scored above 80.",
  "Show students from Kolkata.",
  "What is the average marks?",
  "Which department has the highest average marks?",
];

export default function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleAsk(q?: string) {
    const finalQuestion = (q ?? question).trim();
    if (!finalQuestion) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await askQuestion(finalQuestion);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  function handleExampleClick(example: string) {
    setQuestion(example);
  }

  return (
    <div className="page">
      <header className="header">
        <div className="container header-inner">
          <span className="logo">DataPilot AI</span>
          <span className="tag">Text-to-SQL</span>
        </div>
      </header>

      <main className="container">
        <section className="section">
          <h2>Ask your database anything</h2>
          <div className="input-row">
            <input
              type="text"
              placeholder="Type your question here..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            />
            <button onClick={() => handleAsk()} disabled={loading}>
              {loading ? "Thinking..." : "Ask AI"}
            </button>
          </div>

          <div className="examples">
            <p className="examples-label">Example questions:</p>
            <div className="examples-list">
              {EXAMPLE_QUESTIONS.map((example) => (
                <button
                  key={example}
                  type="button"
                  className="example-chip"
                  onClick={() => handleExampleClick(example)}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </section>

        {error && (
          <section className="section">
            <div className="error">{error}</div>
          </section>
        )}

        {result && (
          <>
            <section className="section">
              <h2>Generated SQL</h2>
              <pre>{result.sql}</pre>
            </section>

            <section className="section">
              <h2>Query Result</h2>
              {result.rows.length === 0 ? (
                <p>No results found.</p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        {result.columns.map((col) => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.map((row, i) => (
                        <tr key={i}>
                          {row.map((cell, j) => (
                            <td key={j}>{String(cell)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
