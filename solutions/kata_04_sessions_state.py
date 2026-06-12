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
