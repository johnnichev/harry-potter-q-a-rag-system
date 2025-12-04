import { useState } from "react";
import AskForm from "./components/AskForm";
import Answer from "./components/Answer";
import { ask, askMeta } from "./api/client";
import { askStream } from "./api/client";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<
    { chunk: string; score: number; index: number }[] | undefined
  >(undefined);
  const [showSources, setShowSources] = useState(false);
  const [stream, setStream] = useState(true);

  const onAsk = async (q: string) => {
    setLoading(true);
    setAnswer("");
    setSources(undefined);
    try {
      if (stream) {
        await askStream(
          q,
          (start) => {
            setSources(start?.sources || []);
          },
          (t) => setAnswer((prev) => (prev ?? "") + t),
          (_end) => {}
        );
      } else {
        const res = await ask(q);
        setAnswer(res);
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
      <div
        style={{
          marginBottom: 16,
          display: "flex",
          alignItems: "center",
          gap: 5,
        }}
      >
        <label style={{ display: "block", marginTop: 8 }}>
          <input
            type="checkbox"
            checked={showSources}
            onChange={(e) => setShowSources(e.target.checked)}
          />
          <span style={{ marginLeft: 6 }}>Show sources</span>
        </label>
        <label style={{ display: "block", marginTop: 8 }}>
          <input
            type="checkbox"
            checked={stream}
            onChange={(e) => setStream(e.target.checked)}
          />
          <span style={{ marginLeft: 6 }}>Stream answer</span>
        </label>
      </div>
      <Answer answer={answer} sources={showSources ? sources : undefined} />
    </div>
  );
}
