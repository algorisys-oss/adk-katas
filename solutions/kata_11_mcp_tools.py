from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

filesystem = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        )
    )
)
root_agent = Agent(
    name="file_agent",
    model="gemini-2.5-flash",
    instruction="Use the filesystem tools to read and list files under /tmp.",
    tools=[filesystem],
)
