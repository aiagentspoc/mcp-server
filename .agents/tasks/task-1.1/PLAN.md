# Implementation Plan - Task 1.1: Package Management Configuration (`pyproject.toml`)

## 1. Context & Task Scope
According to [ROADMAP.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md) and [SPECIFICATIONS.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md), Task 1.1 establishes the reproducible Python 3.10+ packaging and dependency management configuration using `pyproject.toml` for `uv` and `pip` workflows.

---

## 2. Prerequisites
- Python 3.10+ runtime environment (CPython 3.11 installed via `uv`).
- `uv` package and project manager installed.

---

## 3. Objectives
1. Define standard PEP 517 / PEP 621 compliant `pyproject.toml`.
2. Configure required runtime dependencies: `fastmcp>=0.1.0`, `pydantic>=2.0.0`.
3. Configure development/testing dependencies: `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `pytest-benchmark>=4.0.0`.
4. Configure console entrypoint for MCP stdio execution (`hse-easy-mock = "server:main"`).
5. Configure pytest options (`testpaths`, `pythonpath`, `asyncio_mode`).
6. Validate environment sync and dependency resolution with `uv lock` / `uv sync`.

---

## 4. Proposed Changes & Specifications

### 4.1 File: `pyproject.toml`
Create `pyproject.toml` at the project root with the following sections:
- `[project]`:
  - `name = "hse-easy-mock-mcp"`
  - `version = "1.0.0"`
  - `description = "Deterministic Mock MCP Server for HSE Easy regulatory compliance and TDI commercial conversion"`
  - `readme = "README.md"`
  - `requires-python = ">=3.10"`
  - `dependencies = ["fastmcp>=0.1.0", "pydantic>=2.0.0"]`
- `[project.scripts]`:
  - `hse-easy-mock = "server:main"`
- `[project.optional-dependencies]` / `[dependency-groups]`:
  - `dev = ["pytest>=8.0.0", "pytest-asyncio>=0.23.0", "pytest-benchmark>=4.0.0"]`
- `[build-system]`:
  - `requires = ["hatchling"]`
  - `build-backend = "hatchling.build"`
- `[tool.pytest.ini_options]`:
  - `asyncio_mode = "auto"`
  - `testpaths = ["tests"]`
  - `pythonpath = ["."]`
- `[tool.hatch.build.targets.wheel]`:
  - `only-include = ["server.py", "models.py", "fixtures"]`

### 4.2 Supporting Files:
- `.gitignore`: Standard Python ignores (`.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `dist/`, `.ruff_cache/`).
- `tests/`: Directory structure initialization for test suite.

---

## 5. Verification Strategy
1. **Dependency Resolution**: Execute `uv lock` and `uv sync` to confirm all dependencies resolve cleanly on Python 3.11.
2. **Environment Verification**: Verify `fastmcp`, `pydantic`, and `pytest` are importable in the virtual environment (`uv run python -c "..."`).
3. **Pytest Sanity Check**: Run `uv run pytest` to ensure the test runner initializes properly.
