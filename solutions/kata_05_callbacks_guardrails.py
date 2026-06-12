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
