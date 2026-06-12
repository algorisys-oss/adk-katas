from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor

search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    instruction="Answer questions using google_search and cite what you find.",
    tools=[google_search],
)
coder_agent = Agent(
    name="coder_agent",
    model="gemini-2.5-flash",
    instruction="Solve numeric/data questions by writing and running Python.",
    code_executor=BuiltInCodeExecutor(),
)
root_agent = search_agent
