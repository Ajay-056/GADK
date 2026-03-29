import os
from ..docker_utils import run_container

def locust_runner(locust_file: str, container_name: str, host: str, users: int, spawn_rate: int, run_time: str) -> dict:
    """Locust-specific runner configuration (headless mode)."""
    pwd = os.getcwd()
    image = "locustio/locust:latest"
    command = [
        "-f", f"/tests/{locust_file}",
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--headless"
    ]
    volumes = {pwd: "/tests"}
    return run_container(image, command, container_name, volumes)
