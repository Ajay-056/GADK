import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

TARGET_FOLDER_PATH = "/home/butcher/"

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='mcp_file_management',
    instruction='You are a helpful file management assistant. You can read_file,read_multiple_files,write_file,edit_file,create_directory,list_directory,move_file,search_files,get_file_info,list_allowed_directories. Be polite and informative. Always start by greeting the user with all your abilities with function parameters',
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    os.path.abspath(TARGET_FOLDER_PATH),
                ],
            ),
        )
    ],
)
