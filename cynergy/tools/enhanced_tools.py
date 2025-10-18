"""Enhanced tools for Cynergy agents including code generation, file operations, etc."""
import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import requests
import aiohttp
from cynergy.core.agent import tool, Tool


@tool(name="execute_python", description="Execute Python code and return the result")
def execute_python(code: str) -> Dict[str, Any]:
    """
    Execute Python code in a safe environment and return the result
    """
    try:
        # Create a temporary file to execute
        import tempfile
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        # Capture the output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            try:
                # Execute the code
                exec_globals = {}
                exec(code, exec_globals)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "stdout": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue()
                }
        
        return {
            "success": True,
            "result": stdout_capture.getvalue(),
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e)
        }


@tool(name="read_file", description="Read the content of a file")
def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read the content of a file with proper error handling
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File does not exist: {file_path}"}
        
        if not path.is_file():
            return {"success": False, "error": f"Path is not a file: {file_path}"}
        
        content = path.read_text(encoding='utf-8')
        return {
            "success": True,
            "content": content,
            "path": str(path.absolute())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "path": file_path
        }


@tool(name="write_file", description="Write content to a file")
def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file with proper error handling
    """
    try:
        path = Path(file_path)
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding='utf-8')
        return {
            "success": True,
            "path": str(path.absolute()),
            "message": f"Successfully wrote {len(content)} characters to {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "path": file_path
        }


@tool(name="list_directory", description="List files and directories in a path")
def list_directory(dir_path: str = ".") -> Dict[str, Any]:
    """
    List files and directories in a given path
    """
    try:
        path = Path(dir_path)
        if not path.exists():
            return {"success": False, "error": f"Directory does not exist: {dir_path}"}
        
        if not path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {dir_path}"}
        
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "path": str(item.absolute())
            })
        
        return {
            "success": True,
            "items": items,
            "path": str(path.absolute())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "path": dir_path
        }


@tool(name="shell_command", description="Execute a shell command safely")
def shell_command(command: str) -> Dict[str, Any]:
    """
    Execute a shell command and return the output
    Note: This is potentially dangerous and should be used carefully
    """
    try:
        # Only allow safe commands (customize as needed)
        dangerous_commands = ["rm", "mv", "dd", "kill", "pkill", "reboot", "shutdown"]
        if any(danger in command for danger in dangerous_commands):
            return {
                "success": False,
                "error": f"Potentially dangerous command blocked: {command}",
                "command": command
            }
        
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30  # 30 second timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "command": command
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds",
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command
        }


@tool(name="search_web", description="Search the web for information")
def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the web for information using a search engine API
    This is a placeholder - in a real implementation, you would connect to a search API
    """
    # Placeholder implementation - in a real system, you'd use an actual search API
    # like Tavily, SerpAPI, or Google Custom Search
    return {
        "success": False,
        "error": "Web search requires a search API key. Please implement with your preferred search service.",
        "query": query,
        "num_results": num_results
    }


@tool(name="calculate", description="Perform mathematical calculations")
def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate mathematical expressions
    """
    try:
        # Only allow mathematical operations
        allowed_chars = set('0123456789+-*/().% ')
        if not all(c in allowed_chars for c in expression):
            return {
                "success": False,
                "error": f"Invalid characters in expression: {expression}"
            }
        
        # Use eval with a safe namespace
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "success": True,
            "result": result,
            "expression": expression
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "expression": expression
        }


@tool(name="code_analyzer", description="Analyze code for common issues and improvements")
def code_analyzer(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code for common issues, best practices, and potential improvements
    """
    issues = []
    
    # Basic checks for Python
    if language.lower() == "python":
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for potential issues
            if 'import os' in line and 'os.system' in code:
                issues.append({
                    "line": i,
                    "type": "security",
                    "description": "Use of os.system() can be a security risk. Consider using subprocess instead."
                })
            
            if 'eval(' in line:
                issues.append({
                    "line": i,
                    "type": "security",
                    "description": "Use of eval() can be a security risk. Consider safer alternatives."
                })
            
            if len(line) > 88:  # PEP 8 line length
                issues.append({
                    "line": i,
                    "type": "style",
                    "description": f"Line exceeds 88 characters ({len(line)} chars). Consider breaking it up."
                })
    
    return {
        "success": True,
        "issues": issues,
        "language": language,
        "total_issues": len(issues),
        "code_length": len(code)
    }


@tool(name="json_validator", description="Validate JSON format")
def json_validator(json_string: str) -> Dict[str, Any]:
    """
    Validate if a string is valid JSON
    """
    try:
        parsed = json.loads(json_string)
        return {
            "success": True,
            "valid": True,
            "parsed_data": parsed,
            "message": "Valid JSON"
        }
    except json.JSONDecodeError as e:
        return {
            "success": True,
            "valid": False,
            "error": str(e),
            "position": e.pos,
            "line": e.lineno,
            "column": e.colno,
            "message": f"Invalid JSON: {str(e)}"
        }


# Register all tools in a registry for easy access
class ToolRegistry:
    """
    Registry to manage and access all available tools
    """
    def __init__(self):
        self.tools = {
            "execute_python": Tool(
                name="execute_python",
                description="Execute Python code and return the result",
                func=execute_python,
                parameters={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to execute"}
                    },
                    "required": ["code"]
                }
            ),
            "read_file": Tool(
                name="read_file",
                description="Read the content of a file",
                func=read_file,
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file to read"}
                    },
                    "required": ["file_path"]
                }
            ),
            "write_file": Tool(
                name="write_file",
                description="Write content to a file",
                func=write_file,
                parameters={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file to write"},
                        "content": {"type": "string", "description": "Content to write to the file"}
                    },
                    "required": ["file_path", "content"]
                }
            ),
            "list_directory": Tool(
                name="list_directory",
                description="List files and directories in a path",
                func=list_directory,
                parameters={
                    "type": "object",
                    "properties": {
                        "dir_path": {"type": "string", "description": "Directory path to list (default is current directory)"}
                    }
                }
            ),
            "shell_command": Tool(
                name="shell_command",
                description="Execute a shell command safely",
                func=shell_command,
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute"}
                    },
                    "required": ["command"]
                }
            ),
            "search_web": Tool(
                name="search_web",
                description="Search the web for information",
                func=search_web,
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results to return (default 5)", "default": 5}
                    },
                    "required": ["query"]
                }
            ),
            "calculate": Tool(
                name="calculate",
                description="Perform mathematical calculations",
                func=calculate,
                parameters={
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
                    },
                    "required": ["expression"]
                }
            ),
            "code_analyzer": Tool(
                name="code_analyzer",
                description="Analyze code for common issues and improvements",
                func=code_analyzer,
                parameters={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to analyze"},
                        "language": {"type": "string", "description": "Programming language (default: python)", "default": "python"}
                    },
                    "required": ["code"]
                }
            ),
            "json_validator": Tool(
                name="json_validator",
                description="Validate JSON format",
                func=json_validator,
                parameters={
                    "type": "object",
                    "properties": {
                        "json_string": {"type": "string", "description": "JSON string to validate"}
                    },
                    "required": ["json_string"]
                }
            )
        }
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_all_tool_names(self) -> List[str]:
        """Get all available tool names"""
        return list(self.tools.keys())
    
    def get_all_tools(self) -> List[Tool]:
        """Get all tools"""
        return list(self.tools.values())


# Create a global registry instance
tool_registry = ToolRegistry()