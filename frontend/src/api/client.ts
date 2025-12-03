const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function ask(question: string): Promise<string> {
  const res = await fetch(`${base}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  })
  if (!res.ok) throw new Error(await res.text())
  return await res.text()
}

export async function askMeta(question: string): Promise<{ answer: string, sources: { chunk: string, score: number, index: number }[] }>{
  const res = await fetch(`${base}/ask_meta`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  })
  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}
