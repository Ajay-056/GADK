import os
from ..docker_utils import run_container

def jmeter_runner(test_plan: str, jtl_file: str, report_name: str, container_name: str) -> dict:
    """JMeter-specific runner configuration."""
    pwd = os.getcwd()
    image = "custmeter:latest"
    command = [
        "-n", "-t", f"/tests/{test_plan}",
        "-l", f"/tests/{jtl_file}",
        "-e", "-o", f"/tests/{report_name}"
    ]
    volumes = {pwd: "/tests"}
    return run_container(image, command, container_name, volumes)
