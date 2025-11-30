import subprocess
import uuid
import os

def start_test(script_path: str) -> str:
    """
    Starts a k6 test in a new Docker container with a unique name.

    Args:
        script_path: The local path to the k6 test script (e.g., 'k6-scripts/test.js').

    Returns:
        A message indicating success with the container name or an error message.
    """
    if not os.path.exists(script_path):
        return f"Error: The script path '{script_path}' does not exist."

    # Get the absolute path and directory of the script
    absolute_script_path = os.path.abspath(script_path)
    script_dir = os.path.dirname(absolute_script_path)
    script_filename = os.path.basename(absolute_script_path)

    # Generate a unique name for the container to allow parallel runs
    container_name = f"k6-test-{uuid.uuid4().hex[:8]}"

    # Command to run k6 in a detached Docker container
    command = [
        "docker", "run",
        "-d", "--rm",
        "--name", container_name,
        "-v", f"{script_dir}:/scripts",
        "grafana/k6", "run", f"/scripts/{script_filename}"
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return f"Successfully started test container '{container_name}'. Container ID: {result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        return f"Error starting k6 container: {error_message}"
    except FileNotFoundError:
        return "Error: 'docker' command not found. Please ensure Docker is installed and in your PATH."

def stop_test(container_name: str) -> str:
    """
    Stops a running k6 test Docker container.

    Args:
        container_name: The name of the Docker container to stop.

    Returns:
        A success or error message.
    """
    if not container_name.startswith("k6-test-"):
        return "Error: For safety, only containers with names starting with 'k6-test-' can be stopped."

    command = ["docker", "stop", container_name]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return f"Successfully stopped test container '{container_name}'."
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        return f"Error stopping container '{container_name}': {error_message}"
    except FileNotFoundError:
        return "Error: 'docker' command not found. Please ensure Docker is installed and in your PATH."

def list_tests() -> str:
    """
    Lists all running k6 test containers.

    Returns:
        A formatted string of running tests or a message if no tests are running.
    """
    # List containers with names starting with 'k6-test-'
    command = [
        "docker", "ps",
        "--filter", "name=k6-test-",
        "--format", "{{.Names}}\\t{{.Status}}"
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        output = result.stdout.strip()
        if not output:
            return "No k6 tests are currently running."
        return f"Running k6 tests:\n{output}"
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        return f"Error listing k6 containers: {error_message}"
    except FileNotFoundError:
        return "Error: 'docker' command not found. Please ensure Docker is installed and in your PATH."
