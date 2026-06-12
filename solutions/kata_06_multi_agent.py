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
