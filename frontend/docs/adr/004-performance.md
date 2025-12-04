# ADR 004: Performance Baseline

## Context
Need baseline metrics and ongoing monitoring.

## Decision
- Measure render and first token timings via app instrumentation
- Track bundle size via `vite build` outputs
- Plan Lighthouse CI integration for future PRs

## Consequences
- Establishes reference metrics for optimization
- Enables tracking improvements over time

