from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from . import tools

# 1. Specialized Tool Agents
jmeter_agent = Agent(
    model='gemini-2.5-flash',
    name='jmeter_specialist',
    description='Specialist for JMeter test configurations.',
    instruction="You handle JMeter specific requests. Use the 'start_jmeter_test' tool.",
    tools=[tools.start_jmeter_test]
)

k6_agent = Agent(
    model='gemini-2.5-flash',
    name='k6_specialist',
    description='Specialist for K6 test configurations.',
    instruction="You handle K6 specific requests. Use the 'start_k6_test' tool.",
    tools=[tools.start_k6_test]
)

locust_agent = Agent(
    model='gemini-2.5-flash',
    name='locust_specialist',
    description='Specialist for Locust test configurations.',
    instruction="You handle Locust specific requests. Use the 'start_locust_test' tool.",
    tools=[tools.start_locust_test]
)

# 2. Infrastructure Specialists
monitoring_agent = Agent(
    model='gemini-2.5-flash',
    name='monitoring_specialist',
    description='Specialist for listing and monitoring active load tests.',
    instruction="List currently running tests across all tools using 'list_running_tests'.",
    tools=[tools.list_running_tests]
)

execution_agent = Agent(
    model='gemini-2.5-flash',
    name='execution_specialist',
    description='General specialist for stopping test containers.',
    instruction="Stop running containers using 'stop_test'. Always require confirmation.",
    tools=[FunctionTool(tools.stop_test, require_confirmation=True)]
)

# 3. Root Orchestrator
orchestrator_agent = Agent(
    model='gemini-2.5-flash',
    name='performance_lead',
    description='Lead Performance Engineer coordinating multi-tool test lifecycles.',
    instruction=(
        "You are the Lead Performance Engineer. You manage specialists for JMeter, K6, and Locust. "
        "1. Delegate tool-specific start requests to 'jmeter_specialist', 'k6_specialist', or 'locust_specialist'. "
        "2. Delegate monitoring/listing requests to 'monitoring_specialist'. "
        "3. Delegate stop requests to 'execution_specialist'. "
        "Always summarize the actions taken by your team for the user."
    ),
    sub_agents=[jmeter_agent, k6_agent, locust_agent, monitoring_agent, execution_agent]
)

root_agent = orchestrator_agent
