import { useState } from "react";
import AskForm from "./components/AskForm";
import Answer from "./components/Answer";
import { ask, askMeta } from "./api/client";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<
    { chunk: string; score: number; index: number }[] | undefined
  >(undefined);
  const [showSources, setShowSources] = useState(false);

  const onAsk = async (q: string) => {
    setLoading(true);
    setAnswer(null);
    setSources(undefined);
    try {
      const res = await ask(q);
      setAnswer(res);
      if (showSources) {
        const meta = await askMeta(q);
        setSources(meta.sources);
      }
    } catch (e: any) {
      setAnswer(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: "0 16px" }}>
      <h1 style={{ margin: 0, marginBottom: 16 }}>Harry Potter Q&A</h1>
      <AskForm onAsk={onAsk} loading={loading} />
      <label style={{ display: "block", marginTop: 8 }}>
        <input
          type="checkbox"
          checked={showSources}
          onChange={(e) => setShowSources(e.target.checked)}
        />
        <span style={{ marginLeft: 6 }}>Show sources</span>
      </label>
      <Answer answer={answer} sources={showSources ? sources : undefined} />
    </div>
  );
}
