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
