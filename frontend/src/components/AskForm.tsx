import { useEffect, useRef, useState } from "react";

type Props = {
  onAsk: (q: string) => Promise<void>;
  loading: boolean;
};

export default function AskForm({ onAsk, loading }: Props) {
  const [q, setQ] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!q.trim()) return;
    const toSend = q;
    setQ("");
    await onAsk(toSend);
    // refocus for quick subsequent questions
    inputRef.current?.focus();
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
        ref={inputRef}
        autoFocus
        style={{ flex: 1, padding: "10px", border: "1px solid #ccc", borderRadius: 6 }}
      />
      <button
        type="submit"
        disabled={loading || !q.trim()}
        aria-busy={loading}
        style={{
          minWidth: 140,
          padding: "10px 14px",
          borderRadius: 6,
          border: loading || !q.trim() ? "1px solid var(--border)" : "1px solid var(--primary)",
          background: loading || !q.trim() ? "var(--panel)" : "var(--primary)",
          color: loading || !q.trim() ? "var(--muted)" : "#fff",
          cursor: loading || !q.trim() ? "default" : "pointer",
          opacity: loading ? 0.9 : (!q.trim() ? 0.7 : 1),
        }}
      >
        {loading ? "Asking…" : "Ask Chapter"}
      </button>
    </form>
  );
}
