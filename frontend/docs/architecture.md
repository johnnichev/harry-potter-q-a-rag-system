# Frontend Architecture Diagram

```mermaid
flowchart TD
  UI[Components: AskForm, Messages] -->|props/state| App
  App --> API[API Client]
  API --> SSE[Stream: /ask]
  App --> Types[Types]
```

