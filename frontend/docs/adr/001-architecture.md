# ADR 001: Frontend Architecture

## Context
Single-page React app fetching streamed answers via SSE. Requirements: scalability, maintainability, SOLID, separation of concerns.

## Decision
- Centralize types in `src/types.ts`
- Encapsulate network calls in `src/api/client.ts`
- Keep presentational components isolated from data layer
- Add lint/typecheck/test/CI pipeline to enforce standards

## Consequences
- Clear module boundaries simplify refactors
- Typed interfaces reduce runtime errors
- CI validates build, types, lint, tests

