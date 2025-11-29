import subprocess
import uuid
import time
import requests
import os

# In-memory dictionary to store running test processes and their state
# In a real-world scenario, you would use a more robust solution like a database.
running_tests = {}
BASE_PORT = 6565

def _find_available_port():
    """Finds an available port starting from BASE_PORT."""
    port = BASE_PORT
    used_ports = {test['port'] for test in running_tests.values()}
    while port in used_ports:
        port += 1
    return port

def start_test(script_path: str) -> str:
    """
    Starts a K6 performance test in a background process.
    The test is started in a paused state.

    Args:
        script_path: The local path to the K6 test script (e.g., 'sample_test.js').

    Returns:
        A string containing the unique Test ID and a confirmation message,
        or an error message if the test could not be started.
    """
    if not os.path.exists(script_path):
        return f"Error: Test script not found at '{script_path}'"

    port = _find_available_port()
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    api_address = f"127.0.0.1:{port}"

    # Command to run K6 with the REST API enabled, starting in a paused state.
    command = [
        "k6", "run", script_path,
        "--address", api_address,
        "--paused"
    ]

    try:
        # Start the K6 process in the background
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Store the process information
        running_tests[test_id] = {
            "process": process,
            "port": port,
            "script": script_path,
            "status": "paused", # Initial state
            "pid": process.pid
        }

        # Give it a moment to start up the API server
        time.sleep(2)

        return f"Successfully started K6 test with ID: {test_id}. The test is currently PAUSED. Use 'resume_test' to begin."
    except FileNotFoundError:
        return "Error: The 'k6' command was not found. Please ensure K6 is installed and in your system's PATH."
    except Exception as e:
        return f"An unexpected error occurred while starting the test: {e}"

def list_tests() -> dict:
    """
    Lists all currently running K6 tests and their statuses.

    Returns:
        A dictionary containing the details of all active tests.
    """
    if not running_tests:
        return {"message": "No tests are currently running."}

    test_details = {}
    for test_id, data in running_tests.items():
        # Check if the process is still running
        if data["process"].poll() is not None:
            # Process has terminated, update status
            data["status"] = "finished"

        test_details[test_id] = {
            "pid": data["pid"],
            "script": data["script"],
            "port": data["port"],
            "status": data["status"]
        }
    return test_details

def stop_test(test_id: str) -> str:
    """
    Stops a running K6 test by terminating its process.

    Args:
        test_id: The unique ID of the test to stop.

    Returns:
        A confirmation message or an error if the test ID is not found.
    """
    if test_id not in running_tests:
        return f"Error: Test with ID '{test_id}' not found."

    test_info = running_tests[test_id]
    try:
        test_info["process"].terminate()  # Send SIGTERM
        test_info["process"].wait(timeout=5)  # Wait for process to terminate
        del running_tests[test_id]
        return f"Successfully stopped test '{test_id}'."
    except subprocess.TimeoutExpired:
        test_info["process"].kill()  # Force kill if it doesn't terminate
        del running_tests[test_id]
        return f"Test '{test_id}' did not respond to termination, forcing it to stop."
    except Exception as e:
        return f"An error occurred while stopping the test: {e}"

def _update_test_status(test_id: str, paused_state: bool) -> str:
    """Helper function to pause or resume a test via the K6 API."""
    if test_id not in running_tests:
        return f"Error: Test with ID '{test_id}' not found."

    test_info = running_tests[test_id]
    port = test_info["port"]
    url = f"http://127.0.0.1:{port}/v1/status"
    action = "pause" if paused_state else "resume"
    new_status = "paused" if paused_state else "running"

    print(paused_state)
    # new_state = "true" if paused_state else "false"

    # if new_state:
    #     running_state = "false"
    # else:
    #     running_state = "true"

    # print("new_state", new_state)
    # print("running_state", running_state)

    try:
        response = requests.patch(url, json={
    "data": {
        "attributes": {
            "paused": paused_state
        }
    }
})
        # response = requests.get(url)
        # response1 = requests.patch(url, json={"running": "true"})
        print(response.json())
        # print(response1.json())
        response.raise_for_status() # Raise an exception for bad status codes
        test_info["status"] = new_status
        return f"Successfully sent {action} signal to test '{test_id}'. New status: {new_status}."
    except requests.exceptions.RequestException as e:
        return f"Error communicating with K6 API for test '{test_id}': {e}"

def pause_test(test_id: str) -> str:
    """
    Pauses a running K6 test using the K6 REST API.

    Args:
        test_id: The unique ID of the test to pause.

    Returns:
        A confirmation message or an error.
    """
    return _update_test_status(test_id, paused_state=True)

def resume_test(test_id: str) -> str:
    """
    Resumes a paused K6 test using the K6 REST API.

    Args:
        test_id: The unique ID of the test to resume.

    Returns:
        A confirmation message or an error.
    """
    return _update_test_status(test_id, paused_state=False)
