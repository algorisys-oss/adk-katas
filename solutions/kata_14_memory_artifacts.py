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
