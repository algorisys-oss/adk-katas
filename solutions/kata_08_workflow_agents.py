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
