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
