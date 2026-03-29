import subprocess
import os
from typing import List, Optional

def run_container(image: str, command: List[str], container_name: str, volumes: Optional[dict] = None) -> dict:
    """
    Generic Docker run utility.

    Args:
        image: The Docker image to use.
        command: List of commands/arguments to pass to the container.
        container_name: The name for the container.
        volumes: Dict of {host_path: container_path} mappings.
    """
    docker_command = ["docker", "run", "--detach", "--name", container_name, "--rm"]
    
    if volumes:
        for host_path, container_path in volumes.items():
            docker_command.extend(["-v", f"{host_path}:{container_path}"])
            
    docker_command.append(image)
    docker_command.extend(command)
    
    try:
        subprocess.run(docker_command, check=True, capture_output=True, text=True)
        return {
            "status": "success",
            "message": f"Container {container_name} started successfully.",
            "container_name": container_name
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Failed to start container {container_name}: {e.stderr or str(e)}"
        }

def stop_container(container_name: str) -> dict:
    """Generic Docker stop utility."""
    try:
        subprocess.run(["docker", "stop", container_name], check=True, capture_output=True, text=True)
        return {"status": "success", "message": f"Successfully stopped container: {container_name}"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Failed to stop container {container_name}: {e.stderr or str(e)}"}

def list_containers(image_pattern: str, container_name: Optional[str] = None) -> dict:
    """Generic Docker list utility filtered by image pattern."""
    command = ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}", "--filter", f"ancestor={image_pattern}"]
    if container_name:
        command.extend(["--filter", f"name={container_name}"])
        
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        output = result.stdout.strip().split('\n')
        if not output or output == ['']:
            return {"status": "success", "message": "No matching containers found.", "containers": []}
        
        containers = []
        for line in output:
            if line:
                name, status, image = line.split('\t')
                containers.append({"container_name": name, "status": status, "image": image})
        
        return {"status": "success", "containers": containers}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Failed to list containers: {e.stderr or str(e)}"}
