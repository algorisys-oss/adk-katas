from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

root_agent = Agent(
    name="portable_bot",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    instruction="You are a helpful assistant.",
)
