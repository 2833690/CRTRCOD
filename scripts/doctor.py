"""CRTRCOD environment doctor.

This script intentionally uses only Python standard library modules so it can run
before `uv sync`. It explains the most common reason the scaffold appears "not
working": dependencies were not installed, usually because PyPI is unreachable.
"""

from __future__ import annotations

import importlib.util
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_IMPORTS = [
    "fastapi",
    "polars",
    "pandas",
    "numpy",
    "duckdb",
    "sqlalchemy",
    "redis",
    "celery",
    "streamlit",
    "plotly",
    "httpx",
    "pytest",
]


@dataclass(frozen=True)
class CheckResult:
    """Single diagnostic check result printed by the doctor command."""

    name: str
    ok: bool
    detail: str

    @property
    def marker(self) -> str:
        return "OK" if self.ok else "FAIL"


def run_command(command: list[str]) -> CheckResult:
    """Run a short command and return a structured result without raising."""

    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=15)
    except FileNotFoundError:
        return CheckResult(" ".join(command), False, "command not found")
    except subprocess.TimeoutExpired:
        return CheckResult(" ".join(command), False, "command timed out")

    output = (completed.stdout or completed.stderr).strip().splitlines()
    detail = output[0] if output else f"exit code {completed.returncode}"
    return CheckResult(" ".join(command), completed.returncode == 0, detail)


def check_pypi_dns() -> CheckResult:
    """Check whether the runtime can resolve PyPI before attempting dependency install."""

    try:
        socket.gethostbyname("pypi.org")
    except OSError as exc:
        return CheckResult("PyPI DNS", False, str(exc))
    return CheckResult("PyPI DNS", True, "pypi.org resolves")


def check_imports() -> list[CheckResult]:
    """Report which runtime dependencies are importable in the current interpreter."""

    results: list[CheckResult] = []
    for module in REQUIRED_IMPORTS:
        found = importlib.util.find_spec(module) is not None
        detail = "installed" if found else "missing; run `uv sync` in a network-enabled environment"
        results.append(CheckResult(f"import {module}", found, detail))
    return results


def check_files() -> list[CheckResult]:
    """Verify important scaffold files exist."""

    paths = [
        "pyproject.toml",
        ".env.example",
        "docker/docker-compose.yml",
        "apps/api/main.py",
        "packages/risk/engine.py",
        "docs/manual_ru.md",
    ]
    return [
        CheckResult(
            f"file {path}", Path(path).exists(), "present" if Path(path).exists() else "missing"
        )
        for path in paths
    ]


def main() -> int:
    """Run diagnostics and return non-zero when critical checks fail."""

    checks = [
        run_command(["uv", "--version"]),
        run_command(["python", "--version"]),
        check_pypi_dns(),
        *check_files(),
        *check_imports(),
    ]

    print("CRTRCOD doctor")
    print("==============")
    for check in checks:
        print(f"[{check.marker}] {check.name}: {check.detail}")

    failed_imports = [
        check for check in checks if check.name.startswith("import ") and not check.ok
    ]
    if failed_imports:
        print("\nDiagnosis:")
        print("Runtime dependencies are missing. Run `uv sync` with working access to PyPI,")
        print("then run `uv run pytest tests/ -v`. If your environment blocks PyPI, configure")
        print("a proxy or internal package mirror before installing dependencies.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
