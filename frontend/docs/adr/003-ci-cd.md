# ADR 003: CI/CD Pipeline

## Context
Automate quality gates across typecheck, lint, build, tests.

## Decision
- GitHub Actions workflow `frontend.yml` runs on push/PR
- Enforce coverage thresholds via Vitest config

## Consequences
- Prevents regressions before merge
- Produces coverage reports for audits

