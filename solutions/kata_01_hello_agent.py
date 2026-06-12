from google.adk.agents import Agent

root_agent = Agent(
    name="greeter",
    model="gemini-2.5-flash",
    instruction=(
        "You are a friendly greeter. Greet the user warmly by name and "
        "ask how you can help today."
    ),
    description="Greets the user.",
)
