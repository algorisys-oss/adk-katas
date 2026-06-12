from google.adk.agents import Agent
from google.adk.tools import LongRunningFunctionTool

def request_approval(amount: int, tool_context) -> dict:
    """Requests human approval for a spend amount.

    Args:
        amount: The amount needing approval.
    """
    return {"status": "pending", "ticket": f"approve-{amount}"}

approval_tool = LongRunningFunctionTool(func=request_approval)

root_agent = Agent(
    name="approver",
    model="gemini-2.5-flash",
    instruction="For any spend, call request_approval and tell the user it is pending.",
    tools=[approval_tool],
)
