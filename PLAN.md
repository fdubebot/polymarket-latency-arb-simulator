# Productization Plan — polymarket-latency-arb-simulator

## Goal
Turn the simulator into a product-ready **research tool** with robust risk controls, reproducible execution, clean configuration, reliable CLI/reporting, and CI quality gates.

## Milestones

### M1 — Planning & Baseline Audit
**Deliverables**
- Expanded plan (this file) with implementation milestones and acceptance criteria.
- Repo audit for gaps: risk controls, config system, output artifacts, docs, CI.

**Acceptance criteria**
- Plan clearly maps each user requirement to implementation work.

---

### M2 — Core Engine Productization (Risk + Stability)
**Deliverables**
- Risk guardrails implemented in simulation:
  - inventory caps
  - forced liquidation / de-risk modes
  - risk budget controls
  - drawdown and position-limit guardrails
- Improved simulation outputs with telemetry and risk event counters.
- Deterministic reproducibility preserved via seed and controlled randomness.

**Acceptance criteria**
- Engine enforces configurable caps and guardrails.
- Forced liquidation/de-risk events are triggered and reflected in metrics.
- Result object includes key risk and telemetry summaries.

---

### M3 — Config/Architecture/CLI
**Deliverables**
- Structured config model with support for:
  - defaults
  - JSON config file
  - environment variables
  - CLI overrides
- Polished CLI with clear help and subcommands.
- Clear artifact output (JSON summary + CSV fills/equity curve).

**Acceptance criteria**
- User can run with `--config`, env vars, and CLI flags together.
- CLI help is discoverable and examples are documented.
- Run artifacts are written to output directory and are machine-readable.

---

### M4 — Reliability, Quality, and DevEx
**Deliverables**
- Robust error handling and logging.
- Basic telemetry/metrics summaries.
- README overhaul (quickstart, architecture, examples, limitations, roadmap).
- `CONTRIBUTING.md`, `LICENSE`, `.gitignore` hygiene.
- CI workflow for tests + lint/static checks.

**Acceptance criteria**
- Clean README and contributor docs exist.
- CI executes successfully on push/PR.
- Lint/static checks and tests are runnable locally.

---

### M5 — Validation & Release-like Finish
**Deliverables**
- Added/expanded tests:
  - unit tests for config/risk behavior
  - integration/e2e-like CLI flow test
- Full verification run with command log + outcomes:
  - tests
  - lint/static checks
  - packaging/build checks
- Representative simulation run summary.
- Commit(s) pushed to `main`.

**Acceptance criteria**
- All quality gates pass locally.
- Representative run produces expected artifacts and metrics.
- Final report includes plan summary, implementation, commit hash, validation, and known risks/next steps.

## Requirement Traceability
- **Plan first** → M1 complete before coding.
- **Risk controls** → M2.
- **Config/env+CLI + reproducibility** → M3 (+ seed handling in M2).
- **CLI/report artifacts** → M3.
- **Reliability/telemetry/package quality** → M4.
- **Docs/CONTRIBUTING/LICENSE/.gitignore/CI** → M4.
- **Testing + full validation + representative run** → M5.
- **Commit/push to main + concise final report** → M5.
