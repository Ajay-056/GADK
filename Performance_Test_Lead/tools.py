import os
from .engine.docker_utils import stop_container, list_containers
from .engine.providers.jmeter import jmeter_runner
from .engine.providers.k6 import k6_runner
from .engine.providers.locust import locust_runner

def start_jmeter_test(test_plan: str, jtl_file: str, report_name: str, container_name: str = None) -> dict:
    """Starts a JMeter test using a Docker container."""
    if not container_name:
        container_name = f"jmeter_{os.urandom(4).hex()}"
    return jmeter_runner(test_plan, jtl_file, report_name, container_name)

def start_k6_test(test_script: str, container_name: str = None) -> dict:
    """Starts a K6 test using a Docker container."""
    if not container_name:
        container_name = f"k6_{os.urandom(4).hex()}"
    return k6_runner(test_script, container_name)

def start_locust_test(locust_file: str, host: str, users: int = 10, spawn_rate: int = 1, run_time: str = "1m", container_name: str = None) -> dict:
    """Starts a Locust test in headless mode using a Docker container."""
    if not container_name:
        container_name = f"locust_{os.urandom(4).hex()}"
    return locust_runner(locust_file, container_name, host, users, spawn_rate, run_time)

def list_running_tests(tool_type: str = None) -> dict:
    """
    Lists currently running load tests.
    
    Args:
        tool_type: Optional tool type to filter (jmeter, k6, locust).
    """
    # Mapping tool_type to image patterns
    image_map = {
        "jmeter": "custmeter:latest",
        "k6": "loadimpact/k6",
        "locust": "locustio/locust"
    }
    
    if tool_type and tool_type.lower() in image_map:
        return list_containers(image_map[tool_type.lower()])
    
    # If no tool_type, search for all three
    all_tests = []
    for tool, pattern in image_map.items():
        res = list_containers(pattern)
        if res["status"] == "success":
            for c in res.get("containers", []):
                c["tool"] = tool
                all_tests.append(c)
                
    return {"status": "success", "tests": all_tests}

def stop_test(container_name: str) -> dict:
    """Stops a running load test container."""
    return stop_container(container_name)
