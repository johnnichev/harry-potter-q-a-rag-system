const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function ask(question: string): Promise<string> {
  const res = await fetch(`${base}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, stream: false, include_sources: false, format: 'text' })
  })
  if (!res.ok) throw new Error(await res.text())
  return await res.text()
}

export async function askMeta(question: string): Promise<{ answer: string, sources: { chunk: string, score: number, index: number }[] }>{
  const res = await fetch(`${base}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, stream: false, include_sources: true, format: 'json' })
  })
  if (!res.ok) throw new Error(await res.text())
  return await res.json()
}

export async function askStream(question: string, onStart: (sources: any) => void, onToken: (t: string) => void, onEnd: (final: any) => void) {
  const res = await fetch(`${base}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
    body: JSON.stringify({ question, stream: true, include_sources: true, format: 'json' })
  })
  if (!res.ok || !res.body) throw new Error(await res.text())
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''
    for (const p of parts) {
      const lines = p.split('\n')
      const eventLine = lines.find(l => l.startsWith('event:')) || ''
      const dataLine = lines.find(l => l.startsWith('data:')) || ''
      const evt = eventLine.replace('event:','').trim()
      const dataRaw = dataLine.replace('data:','').trim()
      let data: any = dataRaw
      try { data = JSON.parse(dataRaw) } catch {}
      if (evt === 'start') onStart(data)
      else if (evt === 'token') onToken(String(data))
      else if (evt === 'end') onEnd(data)
    }
  }
}
