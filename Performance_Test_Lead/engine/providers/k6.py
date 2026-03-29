import os
from ..docker_utils import run_container

def k6_runner(test_script: str, container_name: str) -> dict:
    """K6-specific runner configuration."""
    pwd = os.getcwd()
    image = "loadimpact/k6:latest"
    command = ["run", f"/tests/{test_script}"]
    volumes = {pwd: "/tests"}
    return run_container(image, command, container_name, volumes)
