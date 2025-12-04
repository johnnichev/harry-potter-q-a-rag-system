import { useEffect, useState } from "react";
import AskForm from "./components/AskForm";
import { askStream } from "./api/client";

type Source = { chunk: string; score: number; index: number };
type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export default function App() {
  const [loading, setLoading] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [theme, setTheme] = useState<string>(
    () => localStorage.getItem("hp_theme") || "dark"
  );

  useEffect(() => {
    try {
      const raw = localStorage.getItem("hp_chat_messages");
      if (raw) setMessages(JSON.parse(raw));
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("hp_chat_messages", JSON.stringify(messages));
    } catch {}
  }, [messages]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("hp_theme", theme);
    } catch {}
  }, [theme]);

  useEffect(() => {
    setTheme("dark");
  }, []);

  const onAsk = async (q: string) => {
    setLoading(true);
    setThinking(true);
    const userMsg: Message = { id: uid(), role: "user", content: q };
    setMessages((prev) => [...prev, userMsg]);
    try {
      let created = false;
      const assistantId = uid();
      let startSources: Source[] = [];
      await askStream(
        q,
        (start) => {
          startSources = start?.sources || [];
        },
        (t) => {
          if (!created) {
            created = true;
            setThinking(false);
            setMessages((prev) => [
              ...prev,
              {
                id: assistantId,
                role: "assistant",
                content: t,
                sources: startSources,
              },
            ]);
          } else {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: m.content + t } : m
              )
            );
          }
        },
        (_end) => {}
      );
    } catch (e: any) {
      const msg = e?.message || String(e);
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "assistant", content: msg },
      ]);
    } finally {
      setThinking(false);
      setLoading(false);
    }
  };

  return (
    <div className="layout single">
      <main className="chat">
        <header className="brand">
          <div className="title">Harry Potter and the Sorcerer's Stone Q&A</div>
          <div className="subtitle">Ask questions strictly from Chapter 1.</div>
        </header>
        <div className="messages">
          {messages.map((m) => (
            <div key={m.id} className={`message ${m.role}`}>
              <div className="bubble">
                <div>{m.content || ""}</div>
                {showSources &&
                  m.role === "assistant" &&
                  m.sources &&
                  m.sources.length > 0 && (
                    <div className="sources">
                      {m.sources.map((s) => (
                        <details key={s.index}>
                          <summary>
                            #{s.index} score {s.score.toFixed(3)}
                          </summary>
                          <pre>{s.chunk}</pre>
                        </details>
                      ))}
                    </div>
                  )}
              </div>
            </div>
          ))}
          {thinking && (
            <div className="message assistant">
              <div className="bubble loading">
                <div className="dots" aria-live="polite" aria-label="Thinking">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="controls">
          <div className="toggles">
            <label>
              <input
                type="checkbox"
                checked={showSources}
                onChange={(e) => setShowSources(e.target.checked)}
              />
              <span style={{ marginLeft: 4 }}>Show sources</span>
            </label>
          </div>
          <div className="suggestions" aria-label="Try these queries">
            {[
              "Who is Harry Potter?",
              "Where do the Dursleys live?",
              "Who leaves Harry at the Dursleys?",
              "What does 'the boy who lived' refer to?",
              "Who are Dumbledore and McGonagall?",
            ].map((s) => (
              <button key={s} className="chip" onClick={() => onAsk(s)}>
                {s}
              </button>
            ))}
          </div>
          <AskForm onAsk={onAsk} loading={loading} />
        </div>
      </main>
    </div>
  );
}
