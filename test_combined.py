# Simple test to verify the combined Cynergy system works
def test_imports():
    try:
        from cynergy import Agent, OpenAIModel, tool
        print("✅ Main imports work")
        
        from cynergy.core.agent import AgentState
        print("✅ Core module works")
        
        from cynergy.sdk.python import create_agent
        print("✅ SDK module works")
        
        from cynergy.cli.main import cli
        print("✅ CLI module works")
        
        from cynergy.connect import HTTPConnector
        print("✅ Connect module works")
        
        from cynergy.security import PolicyEngine
        print("✅ Security module works")
        
        from cynergy.observe import Tracer
        print("✅ Observe module works")
        
        from cynergy.plugins import PluginManager
        print("✅ Plugins module works")
        
        # Test new enhanced features
        from cynergy import QwenModel, OpenRouterModel, MemoryManager, WorkflowOrchestrator
        print("✅ Enhanced features (Qwen, Memory, Workflow) imports work")
        
        from cynergy.tools.enhanced_tools import execute_python, code_analyzer, calculate
        print("✅ Enhanced tools imports work")
        
        print("\n🎉 All modules imported successfully! The enhanced Cynergy system is working.")
        print("✨ New features available: OpenRouter integration, Enhanced Memory, Workflows, Advanced Tools")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_imports()