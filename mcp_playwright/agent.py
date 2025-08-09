import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='hello_world',
    instruction='You are a helpful playwright assistant. You can perform action with the tools given to you. Be polite and informative. Always start by greeting the user with all your abilities',
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@playwright/mcp@latest",
                ],
            ),
        )
    ],
)
