# CRTRCOD v2 Stability Plan

This document records the practical stability improvements expected before production use.

## Stability priorities

1. Keep all order flow behind `RiskEngine.validate_order()`.
2. Keep every live-trading transition behind explicit operator approval.
3. Treat unavailable data as unsafe and reject orders.
4. Keep dependency installation reproducible through `uv` and CI.
5. Preserve full audit history for kill-switch and risk decisions.

## Local validation sequence

```bash
uv sync
uv run ruff check .
uv run mypy packages/ apps/ --ignore-missing-imports
uv run pytest tests/ -v
```

## Operational rule

If any check fails, do not enable live trading. Fix the failure, rerun the full validation sequence, and record the result in the operator checklist.
