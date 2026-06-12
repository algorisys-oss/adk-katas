"""Shared utilities for the ADK katas.

Import everything in a notebook's setup cell:

    from kata_helpers import *

It gives you:
  - load_env()        : load .env (API key) once
  - has_api_key()     : True if a Gemini key / Vertex config is present
  - run_agent(...)    : run an Agent end-to-end and capture its trajectory
  - tool_calls_of(r)  : list of tool names the agent called
  - check(label, cond): pretty ✅/❌ assertion for "check cells"
  - grade(results)    : summarise a list of check() results
  - requires_key(fn)  : run fn only if a key is set, else print a skip notice

Most katas can be completed and graded WITHOUT an API key — the offline checks
call your functions directly. Only the "run it live" cells need a key.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Make this folder importable (so `import tools...` and `import solutions...`
# work regardless of the notebook's working directory).
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

__all__ = [
    "load_env",
    "has_api_key",
    "run_agent",
    "tool_calls_of",
    "RunResult",
    "check",
    "grade",
    "requires_key",
]


def load_env() -> None:
    """Load environment variables from adk-katas/.env (idempotent)."""
    if (_HERE / ".env").exists():
        load_dotenv(_HERE / ".env", override=False)
    load_dotenv(override=False)  # also pick up an already-exported env / CWD .env


_PLACEHOLDER_KEYS = {"", "PASTE_YOUR_API_KEY_HERE", "your_key_here"}


def has_api_key() -> bool:
    """True if a Google AI Studio key or Vertex AI config looks present."""
    load_env()
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if key and key not in _PLACEHOLDER_KEYS:
        return True
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").upper() == "TRUE" and os.getenv(
        "GOOGLE_CLOUD_PROJECT"
    ):
        return True
    return False


@dataclass
class RunResult:
    """The outcome of running an agent on one prompt."""

    text: str = ""
    tool_calls: list[str] = field(default_factory=list)
    tool_args: list[dict] = field(default_factory=list)
    transfers: list[str] = field(default_factory=list)
    state: dict = field(default_factory=dict)
    author_path: list[str] = field(default_factory=list)

    def __repr__(self) -> str:  # nice notebook output
        calls = ", ".join(self.tool_calls) or "(none)"
        xfer = " -> ".join(self.transfers)
        head = f"RunResult(tools=[{calls}]"
        if xfer:
            head += f", transfers={xfer}"
        return head + f")\n  text: {self.text!r}"


async def run_agent(agent, prompt: str, state: dict | None = None) -> RunResult:
    """Run `agent` on `prompt` and capture what it did.

    Needs an API key (it calls the model). Returns a RunResult with the final
    text plus the tool-call trajectory and any agent transfers — handy for both
    eyeballing and asserting behaviour.
    """
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    app_name = "kata"
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=app_name, user_id="learner", state=state or {}
    )
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)

    result = RunResult()
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id="learner", session_id=session.id, new_message=message
    ):
        if event.author and (not result.author_path or result.author_path[-1] != event.author):
            result.author_path.append(event.author)
        for call in event.get_function_calls() or []:
            if call.name == "transfer_to_agent":
                target = (call.args or {}).get("agent_name", "?")
                result.transfers.append(target)
            else:
                result.tool_calls.append(call.name)
                result.tool_args.append(dict(call.args or {}))
        if event.is_final_response() and event.content and event.content.parts:
            texts = [p.text for p in event.content.parts if p.text]
            if texts:
                result.text = "".join(texts).strip()

    refreshed = await session_service.get_session(
        app_name=app_name, user_id="learner", session_id=session.id
    )
    result.state = dict(refreshed.state) if refreshed else {}
    return result


def tool_calls_of(result: RunResult) -> list[str]:
    """The ordered list of (non-transfer) tool names the agent called."""
    return list(result.tool_calls)


def check(label: str, condition: bool, detail: str = "") -> bool:
    """Print a pretty pass/fail line and return the boolean (for grade())."""
    mark = "✅" if condition else "❌"
    suffix = f"  — {detail}" if detail and not condition else ""
    print(f"{mark} {label}{suffix}")
    return bool(condition)


def grade(results: list[bool]) -> bool:
    """Summarise a list of check() results; returns True if all passed."""
    passed = sum(1 for r in results if r)
    total = len(results)
    allgreen = passed == total
    banner = "🎉 KATA COMPLETE" if allgreen else "🔧 keep going"
    print(f"\n{banner} — {passed}/{total} checks passed")
    return allgreen


def requires_key(fn):
    """Call fn() only if an API key is configured; else print a skip notice."""
    if has_api_key():
        return fn()
    print(
        "⏭️  No API key set — skipping the live model run.\n"
        "    Add GOOGLE_API_KEY to adk-katas/multi_tool_agent/.env (or export it) "
        "to run this cell.\n"
        "    The offline checks above already verify your logic."
    )
    return None
