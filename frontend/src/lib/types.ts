export type Source = { chunk: string; score: number; index: number };
export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};
export type SSEStartPayload = { sources?: Source[] };
export type SSEEndPayload = {};
