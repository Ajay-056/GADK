import os
from google.adk.agents import LlmAgent
from . import prompt
from . tools import k6_manager

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='k6_test_manager_agent',
    instruction='prompt.ROOT_PROMPT',
    tools=[
        k6_manager.start_test,
        k6_manager.stop_test,
        k6_manager.list_tests

    ],
)
