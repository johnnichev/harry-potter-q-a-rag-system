import { useState } from "react";

type Props = {
  onAsk: (q: string) => Promise<void>;
  loading: boolean;
};

export default function AskForm({ onAsk, loading }: Props) {
  const [q, setQ] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!q.trim()) return;
    await onAsk(q);
  };

  return (
    <form
      onSubmit={handleSubmit}
      aria-label="Ask a question"
      style={{ display: "flex", gap: 8, alignItems: "center" }}
    >
      <input
        id="question-input"
        aria-label="Question"
        placeholder="Ask the chapter"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        disabled={loading}
        autoFocus
        style={{ flex: 1, padding: "10px", border: "1px solid #ccc", borderRadius: 6 }}
      />
      <button
        type="submit"
        disabled={loading || !q.trim()}
        aria-busy={loading}
        style={{ minWidth: 140, padding: "10px 14px", borderRadius: 6, border: "1px solid #1a73e8", background: "#1a73e8", color: "#fff" }}
      >
        {loading ? "Asking…" : "Ask Chapter"}
      </button>
    </form>
  );
}
