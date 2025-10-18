"""
Studio module for Cynergy - Web UI for agent design and monitoring
"""
from typing import Dict, Any, Optional
from .api.workflow_api import create_app
import uvicorn


def start_studio(host: str = "127.0.0.1", port: int = 3000):
    """Start the studio server (for CLI use)"""
    app = create_app()
    uvicorn.run(app, host=host, port=port)


# For backward compatibility
def run_studio(host: str = "127.0.0.1", port: int = 3000):
    """Start the studio server (alternative function name)"""
    start_studio(host, port)