"""
Connectors module for Cynergy
"""
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
import aiohttp
import asyncio


class BaseConnector(ABC):
    """Base class for all connectors"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
    
    @abstractmethod
    async def connect(self):
        """Establish connection"""
        pass
    
    @abstractmethod
    async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute an operation"""
        pass


class HTTPConnector(BaseConnector):
    """HTTP connector for API calls"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.base_url = config.get("base_url", "")
        self.headers = config.get("headers", {})
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self):
        """Create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers=self.headers
            )
    
    async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute HTTP request"""
        if not self.session:
            await self.connect()
        
        method = params.get("method", "GET").upper()
        endpoint = params.get("endpoint", "")
        data = params.get("data", {})
        headers = params.get("headers", {})
        
        url = f"{self.base_url}{endpoint}" if endpoint.startswith("/") else f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                result = await response.json()
                return result
        except Exception as e:
            raise Exception(f"HTTP request failed: {str(e)}")
    
    def to_tool(self):
        """Convert connector to a tool"""
        from cynergy.core.agent import Tool
        return Tool(
            name=f"http_{self.name}",
            description=f"HTTP API connector for {self.name}",
            func=self.execute,
            parameters={
                "type": "object",
                "properties": {
                    "operation": {"type": "string"},
                    "params": {"type": "object"}
                },
                "required": ["operation", "params"]
            }
        )


class DatabaseConnector(BaseConnector):
    """Database connector"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.connection_string = config.get("connection_string", "")
        self.driver = config.get("driver", "postgresql")
    
    async def connect(self):
        """Connect to database"""
        # Implementation would depend on the specific database driver
        pass
    
    async def execute(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute database operation"""
        # Implementation would depend on the specific database driver
        pass
    
    def to_tool(self):
        """Convert connector to a tool"""
        from cynergy.core.agent import Tool
        return Tool(
            name=f"db_{self.name}",
            description=f"Database connector for {self.name}",
            func=self.execute,
            parameters={
                "type": "object",
                "properties": {
                    "operation": {"type": "string"},
                    "params": {"type": "object"}
                },
                "required": ["operation", "params"]
            }
        )


# Connector registry
class ConnectorRegistry:
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
    
    def register(self, connector: BaseConnector):
        self.connectors[connector.name] = connector
    
    def get(self, name: str) -> Optional[BaseConnector]:
        return self.connectors.get(name)
    
    async def execute(self, name: str, operation: str, params: Dict[str, Any]) -> Any:
        connector = self.get(name)
        if not connector:
            raise ValueError(f"Connector {name} not found")
        return await connector.execute(operation, params)


# Global registry instance
registry = ConnectorRegistry()