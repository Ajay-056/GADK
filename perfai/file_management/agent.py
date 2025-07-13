from google.adk.agents import Agent
import os
from typing import List

def list_directory(path: str = ".") -> List[str]:
        """Lists files and directories in the given path."""
        try:
            items = os.listdir(path)
            return [os.path.join(path, item) for item in items]
        except FileNotFoundError:
            return [f"Error: Directory not found at {path}"]
        except Exception as e:
            return [f"Error listing directory: {e}"]

def view_file_content(file_path: str) -> str:
    """Reads and returns the content of a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error viewing file: {e}"

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='file_management',
    description='A helpful assistant for user file management operations.',
    instruction='You are a helpful file management assistant. You can list directories, view file contents and show it to user even if it is long not just read. Be polite and informative.',
    output_key="output_response",
    tools=[list_directory, view_file_content]
)
