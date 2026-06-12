"""FastAPI backend for the ADK katas React app.

Endpoints (all under /api):
  GET  /api/health                 -> {ok, has_api_key, adk_version}
  GET  /api/katas                  -> [{id, slug, title, blurb, ...}]
  GET  /api/katas/{slug}           -> full kata (concept, task, starter, solution)
  POST /api/katas/{slug}/check     -> run the learner's code through the graders
  POST /api/katas/{slug}/chat      -> run the learner's agent live (needs API key)

Run it:
  uv run uvicorn server:app --reload --port 8001     # from adk-katas/

NOTE: /check and /chat exec the submitted code in-process. This is a LOCAL,
single-user learning tool — it runs your own code on your own machine. Do not
expose it to untrusted users.
"""

from __future__ import annotations

import google.adk
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from kata_content import BY_SLUG, KATAS, Kata
from kata_helpers import has_api_key, run_agent

app = FastAPI(title="ADK Katas", version="1.0.0")

# The Vite dev server runs on 5173/5174; allow it (and any localhost) in dev.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #
class CheckRequest(BaseModel):
    code: str


class ChatRequest(BaseModel):
    code: str
    prompt: str


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _kata_or_404(slug: str) -> Kata:
    kata = BY_SLUG.get(slug)
    if kata is None:
        raise HTTPException(status_code=404, detail=f"No kata '{slug}'")
    return kata


def _exec_user_code(code: str) -> tuple[dict | None, str | None]:
    """Exec learner code in a fresh namespace; return (namespace, error)."""
    ns: dict = {}
    try:
        exec(compile(code, "<kata-user-code>", "exec"), ns)  # noqa: S102
        return ns, None
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "has_api_key": has_api_key(),
        "adk_version": google.adk.__version__,
        "kata_count": len(KATAS),
    }


@app.get("/api/katas")
def list_katas() -> list[dict]:
    return [
        {"id": k.id, "slug": k.slug, "title": k.title, "blurb": k.blurb}
        for k in KATAS
    ]


@app.get("/api/katas/{slug}")
def get_kata(slug: str) -> dict:
    kata = _kata_or_404(slug)
    data = kata.meta()
    data["solution_code"] = kata.solution_code  # frontend hides until revealed
    return data


@app.post("/api/katas/{slug}/check")
def check_kata(slug: str, req: CheckRequest) -> dict:
    kata = _kata_or_404(slug)
    ns, err = _exec_user_code(req.code)
    if err is not None:
        return {"ok": False, "error": err, "results": []}
    try:
        results = kata.run_checks(ns)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"checker error: {type(e).__name__}: {e}", "results": []}
    payload = [r.as_dict() for r in results]
    all_passed = bool(payload) and all(r["passed"] for r in payload)
    return {"ok": all_passed, "error": None, "results": payload}


@app.post("/api/katas/{slug}/chat")
async def chat_kata(slug: str, req: ChatRequest) -> dict:
    kata = _kata_or_404(slug)
    if not kata.chattable:
        raise HTTPException(status_code=400, detail="This kata has no chat agent.")
    if not has_api_key():
        return {
            "ok": False,
            "needs_key": True,
            "error": "No GOOGLE_API_KEY configured on the backend.",
        }
    ns, err = _exec_user_code(req.code)
    if err is not None:
        return {"ok": False, "error": err}
    agent = ns.get(kata.chat_symbol)
    if agent is None:
        return {"ok": False, "error": f"Your code did not define `{kata.chat_symbol}`."}
    try:
        result = await run_agent(agent, req.prompt)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return {
        "ok": True,
        "text": result.text,
        "tool_calls": result.tool_calls,
        "tool_args": result.tool_args,
        "transfers": result.transfers,
        "author_path": result.author_path,
        "state": result.state,
    }
