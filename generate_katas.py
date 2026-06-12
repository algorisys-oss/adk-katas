"""Generate the Jupyter-notebook frontend for the katas.

Notebooks are derived from `kata_content` (the single source of truth) so they
never drift from the React app or the backend graders. Each kata becomes
`notebooks/kata_NN_slug.ipynb` and a reference `solutions/kata_NN_slug.py`.

    uv run python generate_katas.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from kata_content import KATAS, Kata

HERE = Path(__file__).resolve().parent
NB_DIR = HERE / "notebooks"
SOL_DIR = HERE / "solutions"

INTRO = """\
# {title}

{blurb}

> Part of the **ADK Katas**. Work top-to-bottom: read the concept, fill in the
> `# TODO`s in the starter cell, then run the **Check** cell — it grades your
> code offline (no API call). The **Run it live** cell needs a `GOOGLE_API_KEY`.
"""

SETUP_SRC = """\
# Setup — run me first
import sys, pathlib
# Make the kata library importable whether opened from adk-katas/ or adk-katas/notebooks/
for _p in (pathlib.Path.cwd(), pathlib.Path.cwd().parent):
    if (_p / "kata_helpers.py").exists() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from kata_helpers import *          # load_env, has_api_key, run_agent, check, grade, requires_key
from kata_content import BY_SLUG

KATA = BY_SLUG["{slug}"]
load_env()
print("API key configured:" , has_api_key())
"""

CHECK_SRC = """\
# ✅ Check your work (offline — grades the symbols you defined above)
results = KATA.run_checks(globals())
grade([check(r.label, r.passed, r.detail) for r in results])
"""

LIVE_SRC = """\
# ▶️ Run it live (needs GOOGLE_API_KEY). Each run is a fresh single-turn session.
agent = globals().get(KATA.chat_symbol)

if not KATA.chattable:
    print("This kata has no chat agent — the Check cell is the goal. 🎯")
elif has_api_key() and agent is not None:
    result = await run_agent(agent, {prompt!r})   # noqa: F704  (top-level await is fine in Jupyter)
    print("Response:", result.text)
    if result.tool_calls:
        print("Tools called:", result.tool_calls, result.tool_args)
    if result.transfers:
        print("Transferred to:", result.transfers)
    if result.state:
        print("Session state:", result.state)
else:
    requires_key(lambda: None)
"""

SOLUTION_MD = """\
---
### Stuck? Reveal the reference solution

<details>
<summary>Show solution</summary>

```python
{solution}
```

</details>

When you're done, try the same kata in the React app's live chat (`./dev.sh`
from the repo root) to watch the tool-call traces.
"""


def build_notebook(kata: Kata) -> nbformat.NotebookNode:
    prompt = kata.sample_prompts[0] if kata.sample_prompts else "Hello!"
    cells = [
        new_markdown_cell(INTRO.format(title=kata.title, blurb=kata.blurb)),
        new_markdown_cell(kata.concept_md),
        new_markdown_cell("## Your task\n\n" + kata.task_md),
        new_code_cell(SETUP_SRC.format(slug=kata.slug)),
        new_code_cell("# ✏️ Your code — fill in the TODOs\n" + kata.starter_code),
        new_code_cell(CHECK_SRC),
        new_code_cell(LIVE_SRC.format(prompt=prompt)),
        new_markdown_cell(SOLUTION_MD.format(solution=kata.solution_code)),
    ]
    nb = new_notebook(cells=cells)
    nb.metadata.update(
        {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "adk_kata": {"id": kata.id, "slug": kata.slug},
        }
    )
    return nb


def main() -> None:
    NB_DIR.mkdir(exist_ok=True)
    SOL_DIR.mkdir(exist_ok=True)
    (SOL_DIR / "__init__.py").write_text("")
    for kata in KATAS:
        stem = f"kata_{kata.id}_{kata.slug.replace('-', '_')}"
        nb = build_notebook(kata)
        nbformat.validate(nb)
        nbformat.write(nb, NB_DIR / f"{stem}.ipynb")
        (SOL_DIR / f"{stem}.py").write_text(kata.solution_code + "\n")
        print(f"  wrote notebooks/{stem}.ipynb + solutions/{stem}.py")
    print(f"\nGenerated {len(KATAS)} notebooks in {NB_DIR}")


if __name__ == "__main__":
    main()
