import { useState } from "react";
import AskForm from "./components/AskForm";
import { askStream } from "./api/client";
import { Message, Source } from "./types";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Switch from "@mui/material/Switch";
import FormControlLabel from "@mui/material/FormControlLabel";
import Chip from "@mui/material/Chip";

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export default function App() {
  const [loading, setLoading] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  const onAsk = async (q: string) => {
    setLoading(true);
    setThinking(true);
    const startTs = performance.now();
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
            console.info(
              "perf:firstTokenMs",
              Math.round(performance.now() - startTs)
            );
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
        () => {}
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
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
      <Container maxWidth="lg" sx={{ px: 0 }}>
        <main className="chat">
          <Paper
            elevation={8}
            sx={{
              borderBottomLeftRadius: 8,
              borderBottomRightRadius: 8,
              borderTopLeftRadius: 0,
              borderTopRightRadius: 0,
            }}
            className="brand"
          >
            <Typography variant="h6" className="title">
              Harry Potter and the Sorcerer's Stone Q&A
            </Typography>
            <Typography variant="body2" className="subtitle">
              Ask questions strictly from Chapter 1.
            </Typography>
          </Paper>
          <Box className="messages">
            {messages.map((m) => (
              <div key={m.id} className={`message ${m.role}`}>
                <Paper
                  className="bubble"
                  sx={{
                    backgroundColor:
                      m.role === "user" ? "primary.dark" : "background.paper",
                    color: m.role === "user" ? "#fff" : "text.primary",
                    borderColor: m.role === "user" ? "primary.dark" : "divider",
                    borderStyle: "solid",
                    borderWidth: 1,
                  }}
                >
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
                </Paper>
              </div>
            ))}
            {thinking && (
              <div className="message assistant">
                <Paper className="bubble loading">
                  <div
                    className="dots"
                    aria-live="polite"
                    aria-label="Thinking"
                  >
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </Paper>
              </div>
            )}
          </Box>
          <Paper elevation={8} className="controls">
            <Box className="toggles">
              <FormControlLabel
                control={
                  <Switch
                    checked={showSources}
                    onChange={(e) => setShowSources(e.target.checked)}
                  />
                }
                label="Show sources"
              />
            </Box>
            <Box className="suggestions" aria-label="Try these queries">
              {[
                "Who is Harry Potter?",
                "Where do the Dursleys live?",
                "Who leaves Harry at the Dursleys?",
                "What does 'the boy who lived' refer to?",
                "Who are Dumbledore and McGonagall?",
                "Who turns into a cat at the beginning?",
                "What device does Dumbledore use to dim the lights?",
                "Who lends Hagrid the motorcycle?",
                "What shape is Harry's scar?",
              ].map((s) => (
                <Chip
                  key={s}
                  label={s}
                  onClick={() => onAsk(s)}
                  clickable
                  variant="outlined"
                />
              ))}
            </Box>
            <AskForm onAsk={onAsk} loading={loading} />
          </Paper>
        </main>
      </Container>
    </div>
  );
}
