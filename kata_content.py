"""Single source of truth for the ADK katas.

Every kata is defined ONCE here: its concept, starter code, reference solution,
the offline checks that grade a learner's code, and sample chat prompts. The
FastAPI backend, the Jupyter-notebook generator, and the React frontend all
consume this module — so the curriculum never drifts between frontends.

A "check" runs OFFLINE (no model call): it receives the namespace produced by
exec'ing the learner's code and asserts on the functions/agents it defines.
Live model behaviour is exercised separately through the chat endpoint.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Callable

# ADK imports used by the graders (construction only — no network).
from google.adk.agents import (
    Agent,
    LoopAgent,
    ParallelAgent,
    SequentialAgent,
)
from google.adk.tools.agent_tool import AgentTool


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class CheckResult:
    label: str
    passed: bool
    detail: str = ""

    def as_dict(self) -> dict:
        return {"label": self.label, "passed": self.passed, "detail": self.detail}


@dataclass
class Kata:
    id: str  # "01"
    slug: str  # "hello-agent"
    title: str
    blurb: str  # one-line summary for the kata list
    concept_md: str  # taught concept (markdown)
    task_md: str  # what the learner must do (markdown)
    starter_code: str  # code with # TODO markers
    solution_code: str  # reference completed code
    chat_symbol: str  # agent variable to chat with (e.g. "root_agent")
    sample_prompts: list[str]
    run_checks: Callable[[dict], list[CheckResult]]
    needs_key_for_chat: bool = True
    chattable: bool = True

    def meta(self) -> dict:
        """JSON-serialisable metadata for the frontend / notebook generator."""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "blurb": self.blurb,
            "concept_md": self.concept_md,
            "task_md": self.task_md,
            "starter_code": self.starter_code,
            "sample_prompts": self.sample_prompts,
            "chat_symbol": self.chat_symbol,
            "chattable": self.chattable,
            "needs_key_for_chat": self.needs_key_for_chat,
        }


def _d(s: str) -> str:
    """Dedent + strip a triple-quoted block."""
    return textwrap.dedent(s).strip("\n")


def _ok(label: str, cond: bool, detail: str = "") -> CheckResult:
    return CheckResult(label=label, passed=bool(cond), detail="" if cond else detail)


# --------------------------------------------------------------------------- #
# Kata 01 — Hello Agent
# --------------------------------------------------------------------------- #
K01_CONCEPT = _d(
    """
    ## Kata 01 — Hello, Agent

    The smallest unit in ADK is an **`Agent`**: an LLM plus an instruction. You
    give it a `name`, a `model`, and an `instruction` (its system prompt), and
    ADK handles the conversation loop for you.

    ```python
    from google.adk.agents import Agent

    root_agent = Agent(
        name="greeter",
        model="gemini-2.5-flash",
        instruction="You greet the user warmly by name.",
    )
    ```

    ADK discovers the agent through a variable conventionally named
    **`root_agent`**.
    """
)
K01_TASK = _d(
    """
    Create an `Agent` and bind it to `root_agent`:
    - `name` must be `"greeter"`
    - `model` must be `"gemini-2.5-flash"`
    - give it an `instruction` that tells it to greet the user warmly by name.
    """
)
K01_STARTER = _d(
    '''
    from google.adk.agents import Agent

    # TODO: build the agent described in the task.
    root_agent = None
    '''
)
K01_SOLUTION = _d(
    '''
    from google.adk.agents import Agent

    root_agent = Agent(
        name="greeter",
        model="gemini-2.5-flash",
        instruction=(
            "You are a friendly greeter. Greet the user warmly by name and "
            "ask how you can help today."
        ),
        description="Greets the user.",
    )
    '''
)


def _check_01(ns: dict) -> list[CheckResult]:
    a = ns.get("root_agent")
    out = [_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent is not an Agent")]
    if isinstance(a, Agent):
        out.append(_ok('name is "greeter"', a.name == "greeter", f"name was {a.name!r}"))
        out.append(_ok('model is "gemini-2.5-flash"', a.model == "gemini-2.5-flash", f"model was {a.model!r}"))
        out.append(_ok("has a non-empty instruction", bool(a.instruction), "instruction is empty"))
    return out


# --------------------------------------------------------------------------- #
# Kata 02 — Function Tools
# --------------------------------------------------------------------------- #
K02_CONCEPT = _d(
    """
    ## Kata 02 — Function Tools

    Agents get superpowers from **tools**. In ADK a tool is just a plain Python
    function with **type hints** and a **docstring** — ADK reads both to build
    the schema the model sees. No decorators required.

    ```python
    def get_weather(city: str) -> dict:
        \"\"\"Returns the weather for a city.

        Args:
            city: The city to look up, e.g. "Tokyo".
        \"\"\"
        ...
    ```

    Pass it via `tools=[get_weather]`.
    """
)
K02_TASK = _d(
    """
    1. Implement `get_weather(city: str) -> dict` so it returns a dict with a
       `"report"` string for at least Tokyo, London and New York.
    2. Build `root_agent` (name `"weather_bot"`, model `"gemini-2.5-flash"`)
       with `get_weather` in its `tools`.
    """
)
K02_STARTER = _d(
    '''
    from google.adk.agents import Agent

    def get_weather(city: str) -> dict:
        """Returns the weather for a city.

        Args:
            city: The city to look up, e.g. "Tokyo".
        """
        # TODO: return a dict like {"report": "The weather in Tokyo is ..."}
        return {}

    # TODO: create root_agent with get_weather as a tool.
    root_agent = None
    '''
)
K02_SOLUTION = _d(
    '''
    from google.adk.agents import Agent

    _SAMPLES = {
        "tokyo": "clear, 28 °C",
        "london": "cloudy, 15 °C",
        "new york": "sunny, 25 °C",
    }

    def get_weather(city: str) -> dict:
        """Returns the weather for a city.

        Args:
            city: The city to look up, e.g. "Tokyo".
        """
        report = _SAMPLES.get(city.lower(), "sunny, 22 °C")
        return {"report": f"The weather in {city} is {report}."}

    root_agent = Agent(
        name="weather_bot",
        model="gemini-2.5-flash",
        instruction="Answer weather questions using the get_weather tool.",
        tools=[get_weather],
    )
    '''
)


def _check_02(ns: dict) -> list[CheckResult]:
    out = []
    fn = ns.get("get_weather")
    out.append(_ok("get_weather is callable", callable(fn), "get_weather is missing"))
    if callable(fn):
        try:
            r = fn("Tokyo")
            out.append(_ok("get_weather('Tokyo') returns a dict", isinstance(r, dict), f"got {type(r).__name__}"))
            out.append(_ok("result has a 'report' string", isinstance(r.get("report"), str) and bool(r.get("report")), f"got {r!r}"))
        except Exception as e:  # noqa: BLE001
            out.append(_ok("get_weather('Tokyo') runs without error", False, repr(e)))
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent is not an Agent"))
    if isinstance(a, Agent):
        names = [getattr(t, "__name__", getattr(t, "name", "")) for t in (a.tools or [])]
        out.append(_ok("get_weather is registered as a tool", "get_weather" in names, f"tools were {names}"))
    return out


# --------------------------------------------------------------------------- #
# Kata 03 — Structured Returns & Errors
# --------------------------------------------------------------------------- #
K03_CONCEPT = _d(
    """
    ## Kata 03 — Structured Returns & Errors

    Tools should return **structured dicts**, not bare strings — the model reads
    the keys to decide what to say. The ADK convention is a `"status"` field:

    ```python
    {"status": "success", "report": "..."}      # happy path
    {"status": "error", "error_message": "..."} # failure the model can relay
    ```

    Returning errors *as data* (instead of raising) lets the model apologise and
    recover gracefully.
    """
)
K03_TASK = _d(
    """
    Implement `get_weather(city)` so that:
    - a **known** city returns `{"status": "success", "report": "..."}`
    - an **unknown** city returns
      `{"status": "error", "error_message": "..."}` (do **not** raise).
    """
)
K03_STARTER = _d(
    '''
    KNOWN = {"tokyo": "clear, 28 °C", "london": "cloudy, 15 °C"}

    def get_weather(city: str) -> dict:
        """Returns the weather for a city as a status dict.

        Args:
            city: The city to look up.
        """
        # TODO: return a success dict for known cities,
        #       and an error dict (status="error") for unknown ones.
        return {}
    '''
)
K03_SOLUTION = _d(
    '''
    KNOWN = {"tokyo": "clear, 28 °C", "london": "cloudy, 15 °C"}

    def get_weather(city: str) -> dict:
        """Returns the weather for a city as a status dict.

        Args:
            city: The city to look up.
        """
        report = KNOWN.get(city.lower())
        if report is None:
            return {
                "status": "error",
                "error_message": f"No weather data for '{city}'.",
            }
        return {"status": "success", "report": f"The weather in {city} is {report}."}
    '''
)


def _check_03(ns: dict) -> list[CheckResult]:
    out = []
    fn = ns.get("get_weather")
    out.append(_ok("get_weather is callable", callable(fn), "get_weather is missing"))
    if not callable(fn):
        return out
    try:
        ok = fn("Tokyo")
        out.append(_ok("known city -> status 'success'", ok.get("status") == "success", f"got {ok!r}"))
        out.append(_ok("known city has a 'report'", bool(ok.get("report")), f"got {ok!r}"))
        bad = fn("Atlantis")
        out.append(_ok("unknown city -> status 'error'", bad.get("status") == "error", f"got {bad!r}"))
        out.append(_ok("error has an 'error_message'", bool(bad.get("error_message")), f"got {bad!r}"))
    except Exception as e:  # noqa: BLE001
        out.append(_ok("get_weather does not raise on unknown city", False, repr(e)))
    return out


# --------------------------------------------------------------------------- #
# Kata 04 — Sessions & State
# --------------------------------------------------------------------------- #
K04_CONCEPT = _d(
    """
    ## Kata 04 — Sessions & State

    Agents remember things across turns via **session state** — a dict scoped to
    the conversation. A tool can read/write it by accepting a `ToolContext`
    parameter (ADK injects it; the model never sees it):

    ```python
    from google.adk.tools.tool_context import ToolContext

    def remember_city(city: str, tool_context: ToolContext) -> dict:
        tool_context.state["favorite_city"] = city
        return {"status": "success"}
    ```

    Setting `output_key="last_reply"` on the agent also stores its final text in
    `state["last_reply"]` automatically.
    """
)
K04_TASK = _d(
    """
    1. Implement `remember_city(city, tool_context)` to save the city into
       `tool_context.state["favorite_city"]` and return a success dict.
    2. Build `root_agent` (name `"memory_bot"`) with that tool and with
       `output_key="last_reply"`.
    """
)
K04_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools.tool_context import ToolContext

    def remember_city(city: str, tool_context: ToolContext) -> dict:
        """Saves the user's favourite city to session state.

        Args:
            city: The city to remember.
        """
        # TODO: write the city into tool_context.state["favorite_city"]
        return {}

    # TODO: build root_agent with remember_city and output_key="last_reply".
    root_agent = None
    '''
)
K04_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools.tool_context import ToolContext

    def remember_city(city: str, tool_context: ToolContext) -> dict:
        """Saves the user's favourite city to session state.

        Args:
            city: The city to remember.
        """
        tool_context.state["favorite_city"] = city
        return {"status": "success", "saved": city}

    root_agent = Agent(
        name="memory_bot",
        model="gemini-2.5-flash",
        instruction="Remember the user's favourite city with remember_city.",
        tools=[remember_city],
        output_key="last_reply",
    )
    '''
)


def _check_04(ns: dict) -> list[CheckResult]:
    out = []
    fn = ns.get("remember_city")
    out.append(_ok("remember_city is callable", callable(fn), "remember_city is missing"))
    if callable(fn):
        # Stand-in tool_context with a real .state dict (no model needed).
        ctx = SimpleNamespace(state={})
        try:
            fn("Tokyo", ctx)
            out.append(_ok("writes state['favorite_city']", ctx.state.get("favorite_city") == "Tokyo", f"state was {ctx.state!r}"))
        except Exception as e:  # noqa: BLE001
            out.append(_ok("remember_city runs", False, repr(e)))
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent is not an Agent"))
    if isinstance(a, Agent):
        out.append(_ok('output_key == "last_reply"', a.output_key == "last_reply", f"output_key was {a.output_key!r}"))
    return out


# --------------------------------------------------------------------------- #
# Kata 05 — Callbacks & Guardrails
# --------------------------------------------------------------------------- #
K05_CONCEPT = _d(
    """
    ## Kata 05 — Callbacks & Guardrails

    **Callbacks** let you hook the agent's lifecycle. A `before_tool_callback`
    runs *just before* a tool executes — return `None` to allow it, or return a
    dict to **short-circuit** the tool with that value (a guardrail).

    ```python
    def block_tool(tool, args, tool_context):
        if args.get("city", "").lower() in BLOCKED:
            return {"status": "error", "error_message": "That city is blocked."}
        return None  # allow
    ```
    """
)
K05_TASK = _d(
    """
    1. Implement `guardrail(tool, args, tool_context)`: if `args["city"]`
       (case-insensitive) is in `BLOCKED`, return an **error dict**; otherwise
       return `None`.
    2. Attach it to `root_agent` via `before_tool_callback=guardrail`.
    """
)
K05_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from tools.city_tools import get_weather

    BLOCKED = {"mordor", "atlantis"}

    def guardrail(tool, args, tool_context):
        # TODO: block weather lookups for any city in BLOCKED by returning
        #       {"status": "error", "error_message": "..."}; otherwise return None.
        return None

    # TODO: build root_agent with tools=[get_weather] and
    #       before_tool_callback=guardrail.
    root_agent = None
    '''
)
K05_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from tools.city_tools import get_weather

    BLOCKED = {"mordor", "atlantis"}

    def guardrail(tool, args, tool_context):
        city = (args or {}).get("city", "")
        if city.lower() in BLOCKED:
            return {
                "status": "error",
                "error_message": f"Weather lookups for '{city}' are blocked.",
            }
        return None

    root_agent = Agent(
        name="guarded_weather_bot",
        model="gemini-2.5-flash",
        instruction="Answer weather questions using get_weather.",
        tools=[get_weather],
        before_tool_callback=guardrail,
    )
    '''
)


def _check_05(ns: dict) -> list[CheckResult]:
    out = []
    g = ns.get("guardrail")
    out.append(_ok("guardrail is callable", callable(g), "guardrail is missing"))
    if callable(g):
        try:
            blocked = g(None, {"city": "Mordor"}, None)
            out.append(_ok("blocked city -> error dict", isinstance(blocked, dict) and blocked.get("status") == "error", f"got {blocked!r}"))
            allowed = g(None, {"city": "Tokyo"}, None)
            out.append(_ok("allowed city -> None", allowed is None, f"got {allowed!r}"))
        except Exception as e:  # noqa: BLE001
            out.append(_ok("guardrail runs", False, repr(e)))
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent is not an Agent"))
    if isinstance(a, Agent):
        out.append(_ok("before_tool_callback is wired", a.before_tool_callback is not None, "before_tool_callback not set"))
    return out


# --------------------------------------------------------------------------- #
# Kata 06 — Multi-Agent Delegation
# --------------------------------------------------------------------------- #
K06_CONCEPT = _d(
    """
    ## Kata 06 — Multi-Agent Delegation

    Big problems are easier with **specialists**. Give a coordinator agent
    `sub_agents`, and ADK lets it **transfer** control (via the built-in
    `transfer_to_agent`) to whichever specialist fits the request. Clear
    `description`s on each sub-agent are what make routing reliable.
    """
)
K06_TASK = _d(
    """
    Build three agents:
    - `weather_agent` — owns `get_weather`, with a clear `description`.
    - `time_agent` — owns `get_current_time`, with a clear `description`.
    - `root_agent` (name `"coordinator"`) with
      `sub_agents=[weather_agent, time_agent]`.
    """
)
K06_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from tools.city_tools import get_weather, get_current_time

    # TODO: weather_agent (tools=[get_weather], with a description)
    weather_agent = None
    # TODO: time_agent (tools=[get_current_time], with a description)
    time_agent = None
    # TODO: root_agent "coordinator" with sub_agents=[weather_agent, time_agent]
    root_agent = None
    '''
)
K06_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from tools.city_tools import get_weather, get_current_time

    M = "gemini-2.5-flash"

    weather_agent = Agent(
        name="weather_agent", model=M,
        description="Reports the weather for a city.",
        instruction="Report the weather using get_weather.",
        tools=[get_weather],
    )
    time_agent = Agent(
        name="time_agent", model=M,
        description="Reports the current local time for a city.",
        instruction="Report the time using get_current_time.",
        tools=[get_current_time],
    )
    root_agent = Agent(
        name="coordinator", model=M,
        description="Routes weather/time questions to specialists.",
        instruction=(
            "Delegate weather questions to weather_agent and time questions to "
            "time_agent. Keep your own replies brief."
        ),
        sub_agents=[weather_agent, time_agent],
    )
    '''
)


def _check_06(ns: dict) -> list[CheckResult]:
    out = []
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent is not an Agent"))
    if isinstance(a, Agent):
        subs = a.sub_agents or []
        names = {s.name for s in subs}
        out.append(_ok("has 2 sub-agents", len(subs) == 2, f"found {len(subs)}"))
        out.append(_ok("sub-agents are weather_agent + time_agent", names == {"weather_agent", "time_agent"}, f"names were {names}"))
        out.append(_ok("every sub-agent has a description", all(s.description for s in subs), "a sub-agent is missing a description"))
    return out


# --------------------------------------------------------------------------- #
# Kata 07 — Agent as a Tool
# --------------------------------------------------------------------------- #
K07_CONCEPT = _d(
    """
    ## Kata 07 — Agent as a Tool

    Sometimes you don't want to *hand off* — you want to **call** another agent
    and get its answer back, like a function. Wrap it in an **`AgentTool`**:

    ```python
    from google.adk.tools.agent_tool import AgentTool

    host = Agent(..., tools=[AgentTool(agent=poet_agent)])
    ```

    Unlike `sub_agents` (which transfers control), `AgentTool` keeps the host in
    charge and returns the sub-agent's output as a tool result.
    """
)
K07_TASK = _d(
    """
    1. Build a `poet_agent` that writes a two-line poem about its input.
    2. Build `root_agent` (name `"host"`) that includes the poet as a tool via
       `AgentTool(agent=poet_agent)`.
    """
)
K07_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools.agent_tool import AgentTool

    # TODO: poet_agent — writes a short 2-line poem about the topic it's given.
    poet_agent = None

    # TODO: root_agent "host" with tools=[AgentTool(agent=poet_agent)]
    root_agent = None
    '''
)
K07_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools.agent_tool import AgentTool

    poet_agent = Agent(
        name="poet_agent",
        model="gemini-2.5-flash",
        description="Writes a short two-line poem about a topic.",
        instruction="Write exactly two lines of playful verse about the topic.",
    )

    root_agent = Agent(
        name="host",
        model="gemini-2.5-flash",
        instruction=(
            "When the user asks for a poem, call the poet_agent tool and relay "
            "its verse."
        ),
        tools=[AgentTool(agent=poet_agent)],
    )
    '''
)


def _check_07(ns: dict) -> list[CheckResult]:
    out = []
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent is not an Agent"))
    if isinstance(a, Agent):
        agent_tools = [t for t in (a.tools or []) if isinstance(t, AgentTool)]
        out.append(_ok("root_agent has an AgentTool", len(agent_tools) >= 1, "no AgentTool in tools"))
        if agent_tools:
            wrapped = getattr(agent_tools[0], "agent", None)
            out.append(_ok("the AgentTool wraps an Agent", isinstance(wrapped, Agent), "AgentTool.agent is not an Agent"))
    return out


# --------------------------------------------------------------------------- #
# Kata 08 — Workflow Agents
# --------------------------------------------------------------------------- #
K08_CONCEPT = _d(
    """
    ## Kata 08 — Workflow Agents

    Not everything should be left to the LLM to route. **Workflow agents** run
    sub-agents on a fixed control-flow:

    - `SequentialAgent` — run sub-agents one after another (a pipeline)
    - `ParallelAgent` — run them concurrently
    - `LoopAgent` — repeat until a condition / max iterations

    They're deterministic orchestration, no model call of their own.
    """
)
K08_TASK = _d(
    """
    Build a `SequentialAgent` named `"writer_pipeline"` whose `sub_agents` are,
    in order: a `drafter` agent then a `reviewer` agent. Bind it to `root_agent`.
    """
)
K08_STARTER = _d(
    '''
    from google.adk.agents import Agent, SequentialAgent

    M = "gemini-2.5-flash"

    # TODO: drafter — writes a first draft from the user's topic.
    drafter = None
    # TODO: reviewer — improves the draft.
    reviewer = None

    # TODO: root_agent = SequentialAgent("writer_pipeline", sub_agents=[drafter, reviewer])
    root_agent = None
    '''
)
K08_SOLUTION = _d(
    '''
    from google.adk.agents import Agent, SequentialAgent

    M = "gemini-2.5-flash"

    drafter = Agent(
        name="drafter", model=M,
        instruction="Write a short first draft about the user's topic.",
        output_key="draft",
    )
    reviewer = Agent(
        name="reviewer", model=M,
        instruction="Improve the draft in state['draft']; return the final text.",
    )
    root_agent = SequentialAgent(
        name="writer_pipeline",
        sub_agents=[drafter, reviewer],
    )
    '''
)


def _check_08(ns: dict) -> list[CheckResult]:
    out = []
    a = ns.get("root_agent")
    out.append(_ok("root_agent is a SequentialAgent", isinstance(a, SequentialAgent), f"got {type(a).__name__}"))
    if isinstance(a, SequentialAgent):
        subs = a.sub_agents or []
        out.append(_ok("has 2 sub-agents", len(subs) == 2, f"found {len(subs)}"))
        if len(subs) == 2:
            out.append(_ok("order is drafter -> reviewer", [s.name for s in subs] == ["drafter", "reviewer"], f"order was {[s.name for s in subs]}"))
    return out


# --------------------------------------------------------------------------- #
# Kata 09 — Evaluation
# --------------------------------------------------------------------------- #
K09_CONCEPT = _d(
    """
    ## Kata 09 — Evaluation

    ADK can **grade** an agent against an `EvalSet` — recorded cases with the
    expected **tool trajectory**. Build cases programmatically from ADK's own
    classes so the schema is always valid.

    ⚠️ Gotcha: `IntermediateData.tool_uses` wants **`types.FunctionCall`**
    objects — *not* `types.Part`. Wrapping in a `Part` silently serialises to
    `{}` and your trajectory check passes vacuously.
    """
)
K09_TASK = _d(
    """
    Build `eval_set`: an `EvalSet` with one `EvalCase` (`eval_id="weather_tokyo"`)
    whose single `Invocation` records a `get_weather(city="Tokyo")` tool call in
    `intermediate_data.tool_uses` — using `types.FunctionCall` (not `Part`).
    """
)
K09_STARTER = _d(
    '''
    from google.genai import types
    from google.adk.evaluation.eval_set import EvalSet
    from google.adk.evaluation.eval_case import EvalCase, Invocation, IntermediateData

    # TODO: build an Invocation for "What's the weather in Tokyo?" whose
    #       intermediate_data.tool_uses = [types.FunctionCall(name=..., args=...)]
    invocation = None

    # TODO: wrap it in an EvalCase(eval_id="weather_tokyo") and an EvalSet.
    eval_set = None
    '''
)
K09_SOLUTION = _d(
    '''
    from google.genai import types
    from google.adk.evaluation.eval_set import EvalSet
    from google.adk.evaluation.eval_case import EvalCase, Invocation, IntermediateData

    invocation = Invocation(
        invocation_id="weather_tokyo_1",
        user_content=types.Content(role="user", parts=[types.Part(text="What's the weather in Tokyo?")]),
        final_response=types.Content(role="model", parts=[types.Part(text="The weather in Tokyo is clear, 28 °C.")]),
        intermediate_data=IntermediateData(
            tool_uses=[types.FunctionCall(name="get_weather", args={"city": "Tokyo"})]
        ),
    )
    eval_set = EvalSet(
        eval_set_id="weather_basics",
        name="weather basics",
        eval_cases=[EvalCase(eval_id="weather_tokyo", conversation=[invocation])],
    )
    '''
)


def _check_09(ns: dict) -> list[CheckResult]:
    from google.genai import types

    out = []
    es = ns.get("eval_set")
    from google.adk.evaluation.eval_set import EvalSet as _ES

    out.append(_ok("eval_set is an EvalSet", isinstance(es, _ES), f"got {type(es).__name__}"))
    if isinstance(es, _ES):
        cases = es.eval_cases or []
        out.append(_ok("has 1 eval case", len(cases) == 1, f"found {len(cases)}"))
        if cases:
            out.append(_ok('eval_id is "weather_tokyo"', cases[0].eval_id == "weather_tokyo", f"got {cases[0].eval_id!r}"))
            try:
                tu = cases[0].conversation[0].intermediate_data.tool_uses
                out.append(_ok("records a tool call", len(tu) == 1, f"found {len(tu)} tool_uses"))
                out.append(_ok("tool_uses[0] is a FunctionCall", isinstance(tu[0], types.FunctionCall), f"got {type(tu[0]).__name__} (did you wrap it in a Part?)"))
                out.append(_ok('the tool is get_weather', getattr(tu[0], "name", None) == "get_weather", f"name was {getattr(tu[0], 'name', None)!r}"))
            except Exception as e:  # noqa: BLE001
                out.append(_ok("trajectory is well-formed", False, repr(e)))
    return out


# =========================================================================== #
# ADVANCED TRACK (katas 10–18)
# =========================================================================== #

# --------------------------------------------------------------------------- #
# Kata 10 — Built-in Tools (Google Search & Code Execution)
# --------------------------------------------------------------------------- #
K10_CONCEPT = _d(
    """
    ## Kata 10 — Built-in Tools

    ADK ships **built-in tools** that run model-side on Gemini:

    - `google_search` — grounded web search
    - `BuiltInCodeExecutor` — the model writes & runs Python to compute answers

    ```python
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor
    ```

    ⚠️ A built-in tool can't be mixed with your own function tools in the **same**
    agent, and you get one built-in per agent — so wrap each in its own agent
    (and compose with `AgentTool`/`sub_agents` if you need both).
    """
)
K10_TASK = _d(
    """
    1. `search_agent` — an `Agent` (name `"search_agent"`) with `tools=[google_search]`.
    2. `coder_agent` — an `Agent` (name `"coder_agent"`) with
       `code_executor=BuiltInCodeExecutor()`.
    3. Bind `root_agent = search_agent`.
    """
)
K10_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor

    # TODO: search_agent with tools=[google_search]
    search_agent = None
    # TODO: coder_agent with code_executor=BuiltInCodeExecutor()
    coder_agent = None

    root_agent = None
    '''
)
K10_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor

    search_agent = Agent(
        name="search_agent",
        model="gemini-2.5-flash",
        instruction="Answer questions using google_search and cite what you find.",
        tools=[google_search],
    )
    coder_agent = Agent(
        name="coder_agent",
        model="gemini-2.5-flash",
        instruction="Solve numeric/data questions by writing and running Python.",
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = search_agent
    '''
)


def _check_10(ns: dict) -> list[CheckResult]:
    from google.adk.code_executors import BuiltInCodeExecutor
    from google.adk.tools.google_search_tool import GoogleSearchTool

    out = []
    sa = ns.get("search_agent")
    out.append(_ok("search_agent is an Agent", isinstance(sa, Agent), "search_agent missing"))
    if isinstance(sa, Agent):
        out.append(_ok("search_agent uses google_search", any(isinstance(t, GoogleSearchTool) for t in (sa.tools or [])), "google_search not in tools"))
    ca = ns.get("coder_agent")
    out.append(_ok("coder_agent is an Agent", isinstance(ca, Agent), "coder_agent missing"))
    if isinstance(ca, Agent):
        out.append(_ok("coder_agent has a BuiltInCodeExecutor", isinstance(ca.code_executor, BuiltInCodeExecutor), f"code_executor was {ca.code_executor!r}"))
    out.append(_ok("root_agent is search_agent", ns.get("root_agent") is sa and sa is not None, "root_agent should be search_agent"))
    return out


# --------------------------------------------------------------------------- #
# Kata 11 — MCP Tools (external tool servers)
# --------------------------------------------------------------------------- #
K11_CONCEPT = _d(
    """
    ## Kata 11 — MCP Toolsets

    The **Model Context Protocol (MCP)** is a standard for exposing tools from an
    external server. ADK's **`McpToolset`** connects to one and surfaces all its
    tools to your agent — no per-tool glue code.

    ```python
    from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
    from mcp import StdioServerParameters

    fs = McpToolset(connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        )
    ))
    ```

    The toolset connects lazily when the agent runs; you just declare it.
    """
)
K11_TASK = _d(
    """
    Build `root_agent` (name `"file_agent"`) whose `tools` include an
    `McpToolset` that launches the filesystem MCP server over **stdio**
    (`npx -y @modelcontextprotocol/server-filesystem /tmp`).
    """
)
K11_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
    from mcp import StdioServerParameters

    # TODO: build the McpToolset for the filesystem server, then the agent.
    filesystem = None
    root_agent = None
    '''
)
K11_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
    from mcp import StdioServerParameters

    filesystem = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            )
        )
    )
    root_agent = Agent(
        name="file_agent",
        model="gemini-2.5-flash",
        instruction="Use the filesystem tools to read and list files under /tmp.",
        tools=[filesystem],
    )
    '''
)


def _check_11(ns: dict) -> list[CheckResult]:
    from google.adk.tools.mcp_tool import McpToolset

    out = []
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent missing"))
    if isinstance(a, Agent):
        out.append(_ok("agent has an McpToolset", any(isinstance(t, McpToolset) for t in (a.tools or [])), "no McpToolset in tools"))
    return out


# --------------------------------------------------------------------------- #
# Kata 12 — Long-Running Tools & Human-in-the-Loop
# --------------------------------------------------------------------------- #
K12_CONCEPT = _d(
    """
    ## Kata 12 — Long-Running Tools (Human-in-the-Loop)

    Some actions don't finish in one turn — they need a human, or an async job.
    Wrap such a function in **`LongRunningFunctionTool`**: it returns an
    *intermediate* result (e.g. `{"status": "pending"}`), the agent pauses, and
    your app resumes it later with the real result.

    ```python
    from google.adk.tools import LongRunningFunctionTool

    approve = LongRunningFunctionTool(func=request_approval)
    ```

    `get_user_choice` is a ready-made built-in long-running tool for asking the
    user to pick an option.
    """
)
K12_TASK = _d(
    """
    1. Write `request_approval(amount: int, tool_context) -> dict` returning
       `{"status": "pending", "ticket": ...}`.
    2. Wrap it as `approval_tool = LongRunningFunctionTool(func=request_approval)`.
    3. Build `root_agent` (name `"approver"`) with `tools=[approval_tool]`.
    """
)
K12_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools import LongRunningFunctionTool

    def request_approval(amount: int, tool_context) -> dict:
        """Requests human approval for a spend amount.

        Args:
            amount: The amount needing approval.
        """
        # TODO: return a pending status dict (don't block).
        return {}

    # TODO: wrap request_approval as a LongRunningFunctionTool and build root_agent.
    approval_tool = None
    root_agent = None
    '''
)
K12_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools import LongRunningFunctionTool

    def request_approval(amount: int, tool_context) -> dict:
        """Requests human approval for a spend amount.

        Args:
            amount: The amount needing approval.
        """
        return {"status": "pending", "ticket": f"approve-{amount}"}

    approval_tool = LongRunningFunctionTool(func=request_approval)

    root_agent = Agent(
        name="approver",
        model="gemini-2.5-flash",
        instruction="For any spend, call request_approval and tell the user it is pending.",
        tools=[approval_tool],
    )
    '''
)


def _check_12(ns: dict) -> list[CheckResult]:
    from google.adk.tools import LongRunningFunctionTool

    out = []
    fn = ns.get("request_approval")
    out.append(_ok("request_approval is callable", callable(fn), "missing"))
    if callable(fn):
        try:
            r = fn(100, None)
            out.append(_ok("returns status 'pending'", isinstance(r, dict) and r.get("status") == "pending", f"got {r!r}"))
        except Exception as e:  # noqa: BLE001
            out.append(_ok("request_approval runs", False, repr(e)))
    tool = ns.get("approval_tool")
    out.append(_ok("approval_tool is a LongRunningFunctionTool", isinstance(tool, LongRunningFunctionTool), f"got {type(tool).__name__}"))
    a = ns.get("root_agent")
    out.append(_ok("root_agent wires the long-running tool", isinstance(a, Agent) and any(isinstance(t, LongRunningFunctionTool) for t in (a.tools or [])), "tool not in agent"))
    return out


# --------------------------------------------------------------------------- #
# Kata 13 — Multi-Provider Models (LiteLLM)
# --------------------------------------------------------------------------- #
K13_CONCEPT = _d(
    """
    ## Kata 13 — Multi-Provider Models with LiteLLM

    ADK isn't Gemini-only. Wrap any of 100+ providers (OpenAI, Anthropic, local
    Ollama, …) with **`LiteLlm`** and pass it as the agent's `model`:

    ```python
    from google.adk.models.lite_llm import LiteLlm

    agent = Agent(model=LiteLlm(model="openai/gpt-4o-mini"), ...)
    ```

    The provider's own API key (e.g. `OPENAI_API_KEY`) is read from the env at
    run time. Construction itself makes no network call.
    """
)
K13_TASK = _d(
    """
    Build `root_agent` (name `"portable_bot"`) whose `model` is a `LiteLlm`
    instance pointing at `"openai/gpt-4o-mini"`.
    """
)
K13_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.models.lite_llm import LiteLlm

    # TODO: set model to a LiteLlm wrapping "openai/gpt-4o-mini".
    root_agent = None
    '''
)
K13_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.models.lite_llm import LiteLlm

    root_agent = Agent(
        name="portable_bot",
        model=LiteLlm(model="openai/gpt-4o-mini"),
        instruction="You are a helpful assistant.",
    )
    '''
)


def _check_13(ns: dict) -> list[CheckResult]:
    from google.adk.models.lite_llm import LiteLlm

    out = []
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent missing"))
    if isinstance(a, Agent):
        out.append(_ok("model is a LiteLlm", isinstance(a.model, LiteLlm), f"model was {type(a.model).__name__}"))
        if isinstance(a.model, LiteLlm):
            out.append(_ok('points at "openai/gpt-4o-mini"', a.model.model == "openai/gpt-4o-mini", f"model id was {a.model.model!r}"))
    return out


# --------------------------------------------------------------------------- #
# Kata 14 — Memory & Artifacts
# --------------------------------------------------------------------------- #
K14_CONCEPT = _d(
    """
    ## Kata 14 — Memory & Artifacts

    Two kinds of persistence beyond session state:

    - **Long-term memory** — recall across *different* sessions. Add the built-in
      `load_memory` tool so the agent can search a `MemoryService`.
    - **Artifacts** — named binary blobs (images, PDFs, files). A tool saves one
      with `tool_context.save_artifact("name", types.Part(...))` and reads it
      back with `tool_context.load_artifact("name")`.

    ```python
    from google.adk.tools import load_memory
    ```
    """
)
K14_TASK = _d(
    """
    1. Write `save_note(text: str, tool_context) -> dict` that saves `text` as an
       artifact called `"note.txt"` via `tool_context.save_artifact(...)`.
    2. Build `root_agent` (name `"memory_bot"`) with
       `tools=[load_memory, save_note]`.
    """
)
K14_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools import load_memory
    from google.genai import types

    def save_note(text: str, tool_context) -> dict:
        """Saves a text note as an artifact named note.txt.

        Args:
            text: The note contents.
        """
        # TODO: tool_context.save_artifact("note.txt", types.Part(text=text))
        return {}

    # TODO: build root_agent with tools=[load_memory, save_note]
    root_agent = None
    '''
)
K14_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.tools import load_memory
    from google.genai import types

    def save_note(text: str, tool_context) -> dict:
        """Saves a text note as an artifact named note.txt.

        Args:
            text: The note contents.
        """
        tool_context.save_artifact("note.txt", types.Part(text=text))
        return {"status": "success", "saved": "note.txt"}

    root_agent = Agent(
        name="memory_bot",
        model="gemini-2.5-flash",
        instruction="Recall past facts with load_memory; save notes with save_note.",
        tools=[load_memory, save_note],
    )
    '''
)


def _check_14(ns: dict) -> list[CheckResult]:
    import inspect as _inspect

    from google.adk.tools.load_memory_tool import LoadMemoryTool

    out = []
    fn = ns.get("save_note")
    out.append(_ok("save_note is callable", callable(fn), "missing"))
    if callable(fn):
        params = list(_inspect.signature(fn).parameters)
        out.append(_ok("save_note takes a tool_context param", "tool_context" in params, f"params were {params}"))
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent missing"))
    if isinstance(a, Agent):
        names = [getattr(t, "__name__", getattr(t, "name", "")) for t in (a.tools or [])]
        out.append(_ok("has the load_memory tool", any(isinstance(t, LoadMemoryTool) for t in (a.tools or [])), f"tools were {names}"))
        out.append(_ok("has the save_note tool", "save_note" in names, f"tools were {names}"))
    return out


# --------------------------------------------------------------------------- #
# Kata 15 — Planners (Plan-and-Act)
# --------------------------------------------------------------------------- #
K15_CONCEPT = _d(
    """
    ## Kata 15 — Planners

    A **planner** makes the agent *think before acting* — draft a plan, then
    execute the steps.

    - **`PlanReActPlanner`** — prompt-based Plan→Reason→Act; works on any model.
    - **`BuiltInPlanner`** — uses Gemini 2.5 native "thinking" (pass a
      `types.ThinkingConfig`).

    ```python
    from google.adk.planners import PlanReActPlanner
    agent = Agent(..., planner=PlanReActPlanner())
    ```
    """
)
K15_TASK = _d(
    """
    Build `root_agent` (name `"planner_bot"`) with `planner=PlanReActPlanner()`
    and the `get_weather` + `get_current_time` tools so it can plan multi-step
    answers.
    """
)
K15_STARTER = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.planners import PlanReActPlanner
    from tools.city_tools import get_weather, get_current_time

    # TODO: build root_agent with a PlanReActPlanner and the two tools.
    root_agent = None
    '''
)
K15_SOLUTION = _d(
    '''
    from google.adk.agents import Agent
    from google.adk.planners import PlanReActPlanner
    from tools.city_tools import get_weather, get_current_time

    root_agent = Agent(
        name="planner_bot",
        model="gemini-2.5-flash",
        instruction="Plan the steps, then use the tools to answer fully.",
        planner=PlanReActPlanner(),
        tools=[get_weather, get_current_time],
    )
    '''
)


def _check_15(ns: dict) -> list[CheckResult]:
    from google.adk.planners import PlanReActPlanner

    out = []
    a = ns.get("root_agent")
    out.append(_ok("root_agent is an Agent", isinstance(a, Agent), "root_agent missing"))
    if isinstance(a, Agent):
        out.append(_ok("planner is a PlanReActPlanner", isinstance(a.planner, PlanReActPlanner), f"planner was {type(a.planner).__name__}"))
        out.append(_ok("has both tools", len(a.tools or []) >= 2, f"found {len(a.tools or [])} tools"))
    return out


# --------------------------------------------------------------------------- #
# Kata 16 — Streaming (SSE & Live)
# --------------------------------------------------------------------------- #
K16_CONCEPT = _d(
    """
    ## Kata 16 — Streaming

    `RunConfig.streaming_mode` controls how output is delivered:

    - **`StreamingMode.SSE`** — token-by-token text streaming (partial events).
    - **`StreamingMode.BIDI`** — full bidirectional **Live** (audio/video), run
      via `runner.run_live(...)`.
    - **`StreamingMode.NONE`** — one final response (the default).

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode
    cfg = RunConfig(streaming_mode=StreamingMode.SSE)
    ```

    With SSE you consume `event.partial` chunks as the model types.
    """
)
K16_TASK = _d(
    """
    Create `run_config = RunConfig(...)` with `streaming_mode` set to
    `StreamingMode.SSE` (token streaming).
    """
)
K16_STARTER = _d(
    '''
    from google.adk.agents.run_config import RunConfig, StreamingMode

    # TODO: build a RunConfig with SSE token streaming.
    run_config = None
    '''
)
K16_SOLUTION = _d(
    '''
    from google.adk.agents.run_config import RunConfig, StreamingMode

    run_config = RunConfig(streaming_mode=StreamingMode.SSE)
    '''
)


def _check_16(ns: dict) -> list[CheckResult]:
    from google.adk.agents.run_config import RunConfig, StreamingMode

    out = []
    cfg = ns.get("run_config")
    out.append(_ok("run_config is a RunConfig", isinstance(cfg, RunConfig), f"got {type(cfg).__name__}"))
    if isinstance(cfg, RunConfig):
        out.append(_ok("streaming_mode is SSE", cfg.streaming_mode == StreamingMode.SSE, f"was {cfg.streaming_mode!r}"))
    return out


# --------------------------------------------------------------------------- #
# Kata 17 — Iterative Refinement (LoopAgent + generator/critic)
# --------------------------------------------------------------------------- #
K17_CONCEPT = _d(
    """
    ## Kata 17 — Iterative Refinement

    A **`LoopAgent`** runs its sub-agents repeatedly until one calls **`exit_loop`**
    (or `max_iterations` is hit). The classic pattern is **generator → critic**:
    the generator drafts, the critic judges and either asks for changes or exits.

    ```python
    from google.adk.agents import LoopAgent
    from google.adk.tools import exit_loop
    ```

    The critic gets `exit_loop` as a tool; calling it sets `escalate` and ends
    the loop.
    """
)
K17_TASK = _d(
    """
    Build:
    - `generator` — drafts text into `output_key="draft"`.
    - `critic` — reviews `state['draft']`; if good enough it calls `exit_loop`,
      else it gives feedback. Give it `tools=[exit_loop]`.
    - `root_agent = LoopAgent(name="refine_loop", sub_agents=[generator, critic],
      max_iterations=3)`.
    """
)
K17_STARTER = _d(
    '''
    from google.adk.agents import Agent, LoopAgent
    from google.adk.tools import exit_loop

    M = "gemini-2.5-flash"

    # TODO: generator (output_key="draft")
    generator = None
    # TODO: critic (tools=[exit_loop])
    critic = None
    # TODO: root_agent = LoopAgent(..., max_iterations=3)
    root_agent = None
    '''
)
K17_SOLUTION = _d(
    '''
    from google.adk.agents import Agent, LoopAgent
    from google.adk.tools import exit_loop

    M = "gemini-2.5-flash"

    generator = Agent(
        name="generator", model=M,
        instruction="Write or revise a short paragraph on the user's topic. "
                    "If feedback is in state, address it.",
        output_key="draft",
    )
    critic = Agent(
        name="critic", model=M,
        instruction="Review state['draft']. If it is clear and complete, call "
                    "exit_loop. Otherwise give one concrete improvement.",
        tools=[exit_loop],
    )
    root_agent = LoopAgent(
        name="refine_loop",
        sub_agents=[generator, critic],
        max_iterations=3,
    )
    '''
)


def _check_17(ns: dict) -> list[CheckResult]:
    out = []
    a = ns.get("root_agent")
    out.append(_ok("root_agent is a LoopAgent", isinstance(a, LoopAgent), f"got {type(a).__name__}"))
    if isinstance(a, LoopAgent):
        out.append(_ok("max_iterations is set", bool(a.max_iterations), f"was {a.max_iterations!r}"))
        subs = a.sub_agents or []
        out.append(_ok("order is generator -> critic", [s.name for s in subs] == ["generator", "critic"], f"order was {[s.name for s in subs]}"))
        critic = next((s for s in subs if s.name == "critic"), None)
        if critic:
            names = [getattr(t, "__name__", getattr(t, "name", "")) for t in (critic.tools or [])]
            out.append(_ok("critic can call exit_loop", "exit_loop" in names, f"critic tools were {names}"))
    return out


# --------------------------------------------------------------------------- #
# Kata 18 — Evaluation Metrics
# --------------------------------------------------------------------------- #
K18_CONCEPT = _d(
    """
    ## Kata 18 — Evaluation Metrics

    Kata 09 recorded a trajectory; now we **score** against it. ADK's evaluation
    config defines `criteria` — pass/fail thresholds per metric:

    - **`tool_trajectory_avg_score`** — did the agent call the right tools, in
      order? (1.0 = exact match)
    - **`response_match_score`** — ROUGE similarity of the final text to the
      reference (e.g. 0.8).

    You run it with `AgentEvaluator.evaluate(...)` — which also drops cleanly
    into a `pytest` test:

    ```python
    from google.adk.evaluation.agent_evaluator import AgentEvaluator
    await AgentEvaluator.evaluate("my_agent_module", "tests/evalset.json")
    ```
    """
)
K18_TASK = _d(
    """
    Define `criteria` — a dict with `tool_trajectory_avg_score` set to `1.0` and
    `response_match_score` set to `0.8` (both floats in 0..1).
    """
)
K18_STARTER = _d(
    '''
    # TODO: define the eval criteria dict (two metrics, float thresholds 0..1).
    criteria = None
    '''
)
K18_SOLUTION = _d(
    '''
    criteria = {
        "tool_trajectory_avg_score": 1.0,
        "response_match_score": 0.8,
    }
    '''
)


def _check_18(ns: dict) -> list[CheckResult]:
    out = []
    c = ns.get("criteria")
    out.append(_ok("criteria is a dict", isinstance(c, dict), f"got {type(c).__name__}"))
    if isinstance(c, dict):
        out.append(_ok("has tool_trajectory_avg_score == 1.0", c.get("tool_trajectory_avg_score") == 1.0, f"got {c.get('tool_trajectory_avg_score')!r}"))
        rm = c.get("response_match_score")
        out.append(_ok("has response_match_score in 0..1", isinstance(rm, (int, float)) and 0 <= rm <= 1, f"got {rm!r}"))
    return out


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
KATAS: list[Kata] = [
    Kata("01", "hello-agent", "Hello, Agent", "Build and run the smallest possible ADK agent.",
         K01_CONCEPT, K01_TASK, K01_STARTER, K01_SOLUTION, "root_agent",
         ["Hi, I'm Rajesh!"], _check_01),
    Kata("02", "function-tools", "Function Tools", "Give an agent a Python function as a tool.",
         K02_CONCEPT, K02_TASK, K02_STARTER, K02_SOLUTION, "root_agent",
         ["What's the weather in Tokyo?"], _check_02),
    Kata("03", "structured-returns", "Structured Returns & Errors", "Return status dicts and handle failures as data.",
         K03_CONCEPT, K03_TASK, K03_STARTER, K03_SOLUTION, "get_weather",
         ["Weather in Atlantis?"], _check_03, chattable=False),
    Kata("04", "sessions-state", "Sessions & State", "Remember things across turns with session state.",
         K04_CONCEPT, K04_TASK, K04_STARTER, K04_SOLUTION, "root_agent",
         ["My favourite city is Tokyo."], _check_04),
    Kata("05", "callbacks-guardrails", "Callbacks & Guardrails", "Intercept tool calls with a before_tool_callback.",
         K05_CONCEPT, K05_TASK, K05_STARTER, K05_SOLUTION, "root_agent",
         ["What's the weather in Mordor?", "What's the weather in London?"], _check_05),
    Kata("06", "multi-agent", "Multi-Agent Delegation", "Route to specialist sub-agents via transfer.",
         K06_CONCEPT, K06_TASK, K06_STARTER, K06_SOLUTION, "root_agent",
         ["Weather and time in Tokyo?"], _check_06),
    Kata("07", "agent-as-tool", "Agent as a Tool", "Call another agent like a function with AgentTool.",
         K07_CONCEPT, K07_TASK, K07_STARTER, K07_SOLUTION, "root_agent",
         ["Write me a poem about the rain."], _check_07),
    Kata("08", "workflow-agents", "Workflow Agents", "Orchestrate sub-agents with a SequentialAgent.",
         K08_CONCEPT, K08_TASK, K08_STARTER, K08_SOLUTION, "root_agent",
         ["Topic: a lighthouse in winter."], _check_08),
    Kata("09", "evaluation", "Evaluation", "Build an EvalSet to grade tool trajectories.",
         K09_CONCEPT, K09_TASK, K09_STARTER, K09_SOLUTION, "eval_set",
         [], _check_09, chattable=False, needs_key_for_chat=False),
    # --- Advanced track ---
    Kata("10", "builtin-tools", "Built-in Tools", "Use google_search and the code executor.",
         K10_CONCEPT, K10_TASK, K10_STARTER, K10_SOLUTION, "root_agent",
         ["What did Google announce about ADK recently?"], _check_10),
    Kata("11", "mcp-tools", "MCP Toolsets", "Connect an external MCP tool server.",
         K11_CONCEPT, K11_TASK, K11_STARTER, K11_SOLUTION, "root_agent",
         [], _check_11, chattable=False, needs_key_for_chat=False),
    Kata("12", "long-running-tools", "Long-Running Tools", "Human-in-the-loop with LongRunningFunctionTool.",
         K12_CONCEPT, K12_TASK, K12_STARTER, K12_SOLUTION, "root_agent",
         [], _check_12, chattable=False, needs_key_for_chat=False),
    Kata("13", "multi-provider-models", "Multi-Provider Models", "Run non-Gemini models via LiteLLM.",
         K13_CONCEPT, K13_TASK, K13_STARTER, K13_SOLUTION, "root_agent",
         [], _check_13, chattable=False, needs_key_for_chat=False),
    Kata("14", "memory-artifacts", "Memory & Artifacts", "Long-term memory and binary artifacts.",
         K14_CONCEPT, K14_TASK, K14_STARTER, K14_SOLUTION, "root_agent",
         [], _check_14, chattable=False, needs_key_for_chat=False),
    Kata("15", "planners", "Planners", "Plan-and-act with PlanReActPlanner.",
         K15_CONCEPT, K15_TASK, K15_STARTER, K15_SOLUTION, "root_agent",
         ["Compare the weather and time in Tokyo vs London."], _check_15),
    Kata("16", "streaming", "Streaming", "SSE token streaming and bidi Live via RunConfig.",
         K16_CONCEPT, K16_TASK, K16_STARTER, K16_SOLUTION, "run_config",
         [], _check_16, chattable=False, needs_key_for_chat=False),
    Kata("17", "iterative-refinement", "Iterative Refinement", "generator/critic LoopAgent with exit_loop.",
         K17_CONCEPT, K17_TASK, K17_STARTER, K17_SOLUTION, "root_agent",
         ["Topic: why backups matter."], _check_17),
    Kata("18", "eval-metrics", "Evaluation Metrics", "Score trajectories and responses with criteria.",
         K18_CONCEPT, K18_TASK, K18_STARTER, K18_SOLUTION, "criteria",
         [], _check_18, chattable=False, needs_key_for_chat=False),
]

BY_SLUG: dict[str, Kata] = {k.slug: k for k in KATAS}
BY_ID: dict[str, Kata] = {k.id: k for k in KATAS}


def run_checks_on_code(kata: Kata, code: str) -> tuple[list[CheckResult], str | None]:
    """Exec `code` in a fresh namespace and run the kata's checks.

    Returns (results, error). `error` is a string if the code failed to import
    at all (syntax / import error), in which case results is empty.
    """
    ns: dict = {}
    try:
        exec(compile(code, f"<kata-{kata.id}>", "exec"), ns)  # noqa: S102
    except Exception as e:  # noqa: BLE001
        return [], f"{type(e).__name__}: {e}"
    try:
        return kata.run_checks(ns), None
    except Exception as e:  # noqa: BLE001
        return [], f"checker error: {type(e).__name__}: {e}"
