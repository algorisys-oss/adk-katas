# ADK Katas

Interactive, hands-on katas for learning **Google's Agent Development Kit
(ADK 2.2.0)** — the latest. Nine progressive exercises, each teaching one
concept: read it, write the code, get it graded, and chat with your agent live.

There are **two frontends over one shared backend**, so the curriculum never
drifts:

| Frontend | What it is | Run it |
|----------|-----------|--------|
| **React app** | Vite + React Router 7 + Zustand + shadcn/ui + Monaco. In-browser editor, offline auto-grader, and a live agent chat with tool-call traces. | `./dev.sh` (repo root) |
| **Jupyter notebooks** | One notebook per kata; same concept, starter, checks, and live cell. | `uv run jupyter lab notebooks` |

Both call the same **single source of truth** — [`kata_content.py`](kata_content.py) —
which defines every kata's concept, starter code, reference solution, and the
offline graders.

## The curriculum

**Foundations (01–09)**

| # | Kata | Concept |
|---|------|---------|
| 01 | Hello, Agent | the minimal `Agent` |
| 02 | Function Tools | typed funcs + docstrings → auto schema |
| 03 | Structured Returns & Errors | `{"status": ...}` dicts, errors as data |
| 04 | Sessions & State | `ToolContext`, `session.state`, `output_key` |
| 05 | Callbacks & Guardrails | `before_tool_callback` to block/allow |
| 06 | Multi-Agent Delegation | coordinator + `sub_agents`, `transfer_to_agent` |
| 07 | Agent as a Tool | `AgentTool` (call an agent like a function) |
| 08 | Workflow Agents | `SequentialAgent` / `ParallelAgent` / `LoopAgent` |
| 09 | Evaluation | build an `EvalSet`, grade tool trajectories |

**Advanced (10–18)**

| # | Kata | Concept |
|---|------|---------|
| 10 | Built-in Tools | `google_search`, `BuiltInCodeExecutor` |
| 11 | MCP Toolsets | connect external tool servers via `McpToolset` |
| 12 | Long-Running Tools | human-in-the-loop with `LongRunningFunctionTool` |
| 13 | Multi-Provider Models | non-Gemini models via `LiteLlm` |
| 14 | Memory & Artifacts | `load_memory` + `tool_context.save_artifact` |
| 15 | Planners | plan-and-act with `PlanReActPlanner` |
| 16 | Streaming | `RunConfig` SSE token streaming + bidi Live |
| 17 | Iterative Refinement | generator/critic `LoopAgent` + `exit_loop` |
| 18 | Evaluation Metrics | `tool_trajectory` / `response_match` criteria |

## Architecture

```
kata_content.py     ← single source of truth (9 katas: concept, starter, solution, checks)
kata_helpers.py     ← run_agent() via ADK Runner, grading helpers, API-key guard
server.py           ← FastAPI: /api/katas, /api/.../check (offline grade), /api/.../chat (live)
generate_katas.py   ← emits notebooks/ + solutions/ from kata_content
tools/city_tools.py ← shared demo tools reused by several katas
frontend/           ← React SPA (talks to the backend at /api via Vite proxy)
notebooks/          ← 9 generated .ipynb (Jupyter frontend)
solutions/          ← reference solution .py per kata
.env                ← your GOOGLE_API_KEY (git-ignored; .env.example is the template)
```

How grading works: the offline **checks** call your functions/agents directly
(no model call — no API key needed). Only the **live chat** needs a key.

## Setup

Prerequisites: [uv](https://docs.astral.sh/uv/) (Python) and Node.js 20+.

```bash
# 1. Python deps (creates a local .venv from the lockfile):
uv sync
# 2. Frontend deps:
cd frontend && npm install && cd ..
# 3. (Live chat only) add a Gemini key — free at https://aistudio.google.com/apikey
cp .env.example .env        # then edit .env:
#      GOOGLE_GENAI_USE_VERTEXAI=FALSE
#      GOOGLE_API_KEY=your_key_here
```

`./dev.sh` will also install the frontend deps on first run, so the minimum to
get going is: `uv sync`, add your key to `.env`, then `./dev.sh`.

## Run — React app

From the **repo root**:

```bash
./dev.sh           # starts FastAPI (:8001) and Vite (:5173) together
```

Open the Vite URL it prints (http://localhost:5173, or the next free port).
Pick a kata, fill the editor, **Run checks**, then switch to **Live chat** to
talk to your agent. Progress is saved in your browser (Zustand + localStorage).

Run the two halves separately if you prefer:

```bash
uv run uvicorn server:app --port 8001 --reload      # backend
cd frontend && npm run dev                           # frontend
```

## Run — Jupyter notebooks

```bash
uv run jupyter lab notebooks
```

Regenerate the notebooks after editing `kata_content.py`:

```bash
uv run python generate_katas.py
```

## Notes

- `server.py` execs your kata code in-process. It's a **local, single-user**
  learning tool — don't expose it to untrusted users.
- Live chat uses the Gemini free tier; a `429 RESOURCE_EXHAUSTED` just means
  you hit the rate limit — wait a minute. The app surfaces this gracefully.
- Tech: ADK 2.2.0, FastAPI, React 19, React Router 7.17, Zustand 5,
  Tailwind v4, shadcn/ui, Monaco, JupyterLab 4.5.
