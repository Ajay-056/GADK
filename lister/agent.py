from google.adk.agents.llm_agent import Agent
from . tools import file_lister

root_agent = Agent(
        model='gemini-2.5-flash',
        name='root_agent',
        description='A File management assistant',
        instruction='You are a file management assistant. When a user provides a directory keyword, use the list_files_tool to retrieve the files. Present the list exactly as the tool returns it. After listing, wait for the user to provide a serial number. Do not perform any other actions until a number is selected.',
        tools=[
            file_lister.list_files_tool
            ]
        )
