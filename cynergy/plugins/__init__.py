"""
Plugins module for Cynergy
"""
from typing import Dict, Any, Callable, List
from abc import ABC, abstractmethod
import importlib


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
    
    @abstractmethod
    def initialize(self):
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the plugin logic"""
        pass


class PluginManager:
    """Manager for loading and executing plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
    
    def register_plugin(self, plugin: BasePlugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        plugin.initialize()
    
    def get_plugin(self, name: str) -> BasePlugin:
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def execute_plugin(self, name: str, data: Any) -> Any:
        """Execute a plugin"""
        plugin = self.get_plugin(name)
        if not plugin:
            raise ValueError(f"Plugin {name} not found")
        return plugin.execute(data)
    
    def load_plugin_from_file(self, file_path: str, plugin_class_name: str, name: str, config: Dict[str, Any]):
        """Dynamically load a plugin from a file"""
        spec = importlib.util.spec_from_file_location("plugin_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        plugin_class = getattr(module, plugin_class_name)
        plugin = plugin_class(name, config)
        self.register_plugin(plugin)
        return plugin


# Example built-in plugins
class CalculatorPlugin(BasePlugin):
    """Simple calculator plugin"""
    
    def initialize(self):
        print(f"Calculator plugin {self.name} initialized")
    
    def execute(self, data: Dict[str, Any]) -> Any:
        operation = data.get("operation")
        a = data.get("a", 0)
        b = data.get("b", 0)
        
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")


class StringProcessorPlugin(BasePlugin):
    """String processing plugin"""
    
    def initialize(self):
        print(f"StringProcessor plugin {self.name} initialized")
    
    def execute(self, data: Dict[str, Any]) -> Any:
        operation = data.get("operation")
        text = data.get("text", "")
        
        if operation == "uppercase":
            return text.upper()
        elif operation == "lowercase":
            return text.lower()
        elif operation == "reverse":
            return text[::-1]
        elif operation == "length":
            return len(text)
        else:
            raise ValueError(f"Unknown operation: {operation}")


# Global plugin manager instance
plugin_manager = PluginManager()