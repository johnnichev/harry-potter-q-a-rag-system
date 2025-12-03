import React from "react";

type Source = { chunk: string; score: number; index: number };

type Props = {
  answer: string | null;
  sources?: Source[];
};

export default function Answer({ answer, sources }: Props) {
  return (
    <div>
      <h2 style={{ margin: 0, marginBottom: 8 }}>Answer</h2>
      <div
        aria-live="polite"
        role="status"
        style={{ border: "1px solid #ddd", padding: 12, minHeight: 100, borderRadius: 6, whiteSpace: "pre-wrap" }}
      >
        {answer || ""}
      </div>

      {sources && sources.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Sources</div>
          {sources.map((s, i) => (
            <div key={i} style={{ borderTop: "1px solid #eee", paddingTop: 8 }}>
              <div style={{ fontSize: 12, color: "#666" }}>Score: {s.score.toFixed(3)} | Chunk #{s.index}</div>
              <div style={{ fontSize: 14, color: "#444", whiteSpace: "pre-wrap" }}>{s.chunk}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
