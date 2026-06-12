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
