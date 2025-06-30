"""
Plugin system for Ageny Online.
System pluginów do rozszerzania funkcjonalności aplikacji.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from fastapi import APIRouter


class PluginInterface(ABC):
    """Interface for Ageny Online plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get plugin description."""
        pass
    
    @abstractmethod
    def get_router(self) -> APIRouter:
        """Get FastAPI router for plugin endpoints."""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration."""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get list of required dependencies."""
        pass


class PluginManager:
    """Manager for Ageny Online plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
    
    def register_plugin(self, plugin: PluginInterface) -> bool:
        """Register a new plugin."""
        try:
            self.plugins[plugin.get_name()] = plugin
            return True
        except Exception as e:
            print(f"Failed to register plugin {plugin.get_name()}: {e}")
            return False
    
    def get_plugin(self, name: str) -> PluginInterface:
        """Get plugin by name."""
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """Get all registered plugins."""
        return self.plugins.copy()
    
    def get_all_routers(self) -> List[APIRouter]:
        """Get all plugin routers."""
        return [plugin.get_router() for plugin in self.plugins.values()]


# Global plugin manager instance
plugin_manager = PluginManager() 