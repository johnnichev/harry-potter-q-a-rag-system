import { Source, SSEStartPayload, SSEEndPayload } from "../types";

const base = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function check(res: Response): Promise<Response> {
  if (!res.ok) throw new Error(await res.text());
  return res;
}

export async function ask(question: string): Promise<string> {
  const res = await fetch(`${base}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      stream: false,
      include_sources: false,
      format: "text",
    }),
  });
  await check(res);
  return await res.text();
}

export async function askMeta(
  question: string
): Promise<{ answer: string; sources: Source[] }> {
  const res = await fetch(`${base}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      stream: false,
      include_sources: true,
      format: "json",
    }),
  });
  await check(res);
  return (await res.json()) as { answer: string; sources: Source[] };
}

export async function askStream(
  question: string,
  onStart: (_payload: SSEStartPayload) => void,
  onToken: (_t: string) => void,
  onEnd: (_payload: SSEEndPayload) => void
) {
  const res = await fetch(`${base}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({
      question,
      stream: true,
      include_sources: true,
      format: "json",
    }),
  });
  if (!res.ok || !res.body) throw new Error(await res.text());
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";
    for (const p of parts) {
      const lines = p.split("\n");
      const eventLine = lines.find((l) => l.startsWith("event:")) || "";
      const dataLine = lines.find((l) => l.startsWith("data:")) || "";
      const evt = eventLine.replace("event:", "").trim();
      const dataRaw = dataLine.replace("data:", "").trim();

      if (evt === "start") {
        let payload: SSEStartPayload = { sources: [] };
        try {
          const parsed = JSON.parse(dataRaw) as {
            sources?: Array<{ chunk: string; score: number; index: number }>;
          };
          if (parsed && Array.isArray(parsed.sources)) {
            const valid = parsed.sources.filter(
              (s) =>
                typeof s?.chunk === "string" &&
                typeof s?.score === "number" &&
                typeof s?.index === "number"
            ) as Source[];
            payload = { sources: valid };
          }
        } catch {
          void 0;
        }
        onStart(payload);
      } else if (evt === "token") {
        let token = dataRaw;
        try {
          const parsed = JSON.parse(dataRaw);
          token = typeof parsed === "string" ? parsed : String(parsed);
        } catch {
          /* empty */
        }
        onToken(token);
      } else if (evt === "end") {
        onEnd({});
      }
    }
  }
}
