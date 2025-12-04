import { useRef, useState } from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

type Props = {
  onAsk: (_question: string) => Promise<void>;
  loading: boolean;
};

export default function AskForm({ onAsk, loading }: Props) {
  const [question, setQuestion] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    const questionToSend = question;
    setQuestion("");
    await onAsk(questionToSend);
    inputRef.current?.focus();
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      aria-label="Ask a question"
      sx={{ display: "flex", gap: 1, alignItems: "center" }}
    >
      <TextField
        inputRef={inputRef}
        autoFocus
        fullWidth
        label="Question"
        placeholder="Ask the chapter"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={loading}
        size="small"
        variant="outlined"
      />
      <Button
        type="submit"
        variant="contained"
        color="primary"
        disabled={loading || !question.trim()}
        aria-busy={loading}
        sx={{ minWidth: 140 }}
      >
        {loading ? "Asking…" : "Ask Chapter"}
      </Button>
    </Box>
  );
}
