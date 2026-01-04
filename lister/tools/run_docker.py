import subprocess
import shlex

def custom_docker_run(command: str):
    """
    Safely executes a 'docker run' command provided by the user.
    Prevents command chaining and shell injection.
    """
    # 1. Basic Security: Remove leading/trailing whitespace
    clean_command = command.strip()

    # 2. Prevent Chaining: Block common shell metacharacters
    forbidden_chars = [";", "&&", "||", "|", "`"]
    if any(char in clean_command for char in forbidden_chars):
        return "Error: Command chaining or redirection is not allowed for security reasons."

    # 3. Validation: Must start with 'docker run'
    if not clean_command.startswith("docker run") or clean_command.startswith("sudo docker run"):
        return "Error: Only 'docker run' commands are permitted."

    try:
        # 4. Secure Parsing: shlex.split handles quotes/escapes correctly
        # It turns "docker run -v '/my path' image" into ['docker', 'run', '-v', '/my path', 'image']
        args = shlex.split(clean_command)

        # 5. Execution: shell=False prevents the OS from interpreting shell commands
        result = subprocess.run(
            args, 
            capture_output=True, 
            text=True, 
            timeout=30, 
            shell=False 
        )

        if result.returncode == 0:
            return f"Success:\n{result.stdout}"
        else:
            return f"Docker Error:\n{result.stderr}"

    except Exception as e:
        return f"An error occurred: {str(e)}"
