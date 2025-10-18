"""
# Cynergy Memory Management Demo

This example demonstrates the advanced memory management capabilities in Cynergy:
1. Conversation memory
2. Episodic memory  
3. Semantic memory
4. Working memory
5. Memory configuration and management
"""

import asyncio
from datetime import datetime
from cynergy import Agent, MemoryManager, ConversationMemory, EpisodicMemory, SemanticMemory, WorkingMemory
from unittest.mock import MagicMock

# Function to create a mock model for demonstration
def create_mock_model():
    """Create a mock model for demonstration when API keys aren't available"""
    mock_model = MagicMock()
    mock_model.generate = MagicMock(return_value=MagicMock(
        content="This is a mock response from the model. In a real implementation, this would connect to an actual AI service.",
        tool_calls=[]
    ))
    return mock_model

async def demo_conversation_memory():
    """Demo conversation memory capabilities"""
    print("🔍 Conversation Memory Demo")
    print("-" * 30)
    
    # Create conversation memory with specific configuration
    conversation_memory = ConversationMemory(
        config={
            "max_turns": 50,
            "compression_enabled": True
        }
    )
    
    # Add some conversation messages
    from cynergy.core.agent import Message
    
    messages = [
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Hello, how are you?"),
        Message(role="assistant", content="I'm doing well, thank you for asking!"),
        Message(role="user", content="What can you help me with today?"),
        Message(role="assistant", content="I can help with a variety of tasks including answering questions, providing information, and using tools.")
    ]
    
    for msg in messages:
        conversation_memory.add_message(msg)
    
    # Get context messages
    context_messages = conversation_memory.get_context_messages()
    print(f"Stored {len(context_messages)} conversation messages")
    
    for i, msg in enumerate(context_messages):
        print(f"  {i+1}. [{msg.role}] {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}")
    
    # Demonstrate memory limits and compression
    print(f"Max turns configured: {conversation_memory.max_turns}")
    print(f"Compression enabled: {conversation_memory.compression_enabled}")
    
    return conversation_memory

async def demo_episodic_memory():
    """Demo episodic memory capabilities"""
    print("\n🔍 Episodic Memory Demo")
    print("-" * 30)
    
    # Create episodic memory
    episodic_memory = EpisodicMemory(
        config={
            "episode_tags": ["task", "session", "interaction", "project"]
        }
    )
    
    # Add some episodic memories
    episodes = [
        ("Completed initial project setup", ["project", "setup"], 0.9),
        ("Discussed requirements with client", ["meeting", "requirements"], 0.7),
        ("Implemented authentication module", ["development", "security"], 0.8),
        ("Fixed critical bug in payment system", ["bug", "payment", "critical"], 1.0),
        ("Weekly team sync meeting", ["meeting", "sync"], 0.6)
    ]
    
    for content, tags, importance in episodes:
        episodic_memory.add_episode(content, tags, importance)
        print(f"✅ Added episode: {content[:30]}{'...' if len(content) > 30 else ''}")
    
    # Retrieve episodes by tags
    important_episodes = episodic_memory.get_episodes_by_tags(["critical", "security"])
    print(f"\nFound {len(important_episodes)} critical/security episodes:")
    for episode in important_episodes:
        print(f"  • {episode.content} (importance: {episode.importance})")
    
    # Retrieve by project tag
    project_episodes = episodic_memory.get_episodes_by_tags(["project"])
    print(f"\nFound {len(project_episodes)} project-related episodes:")
    for episode in project_episodes:
        print(f"  • {episode.content}")
    
    return episodic_memory

async def demo_semantic_memory():
    """Demo semantic memory capabilities"""
    print("\n🔍 Semantic Memory Demo")
    print("-" * 30)
    
    # Create semantic memory
    semantic_memory = SemanticMemory(
        config={
            "relevance_threshold": 0.5,
            "embedding_dim": 384
        }
    )
    
    # Add some semantic knowledge
    knowledge_items = [
        ("Python is a high-level, interpreted programming language", ["programming", "language", "python"], None),
        ("Machine learning involves training algorithms on data", ["ai", "ml", "algorithms"], None),
        ("Cynergy is an agentic AI development platform", ["cynergy", "ai", "platform"], None),
        ("Agentic AI refers to AI systems that can take autonomous actions", ["ai", "agentic", "autonomous"], None),
        ("Large language models are trained on vast amounts of text", ["llm", "ai", "training"], None)
    ]
    
    for content, tags, embedding in knowledge_items:
        semantic_memory.add_knowledge(content, tags, embedding)
        print(f"✅ Added knowledge: {content[:40]}{'...' if len(content) > 40 else ''}")
    
    # Search for relevant knowledge
    search_results = semantic_memory.search_similar("What is Cynergy?", top_k=3)
    print(f"\nSearch results for 'What is Cynergy?' ({len(search_results)} found):")
    for result in search_results:
        print(f"  • {result.content}")
    
    # Search for Python-related knowledge
    python_results = semantic_memory.search_similar("Python programming", top_k=3)
    print(f"\nSearch results for 'Python programming' ({len(python_results)} found):")
    for result in python_results:
        print(f"  • {result.content}")
    
    return semantic_memory

async def demo_working_memory():
    """Demo working memory capabilities"""
    print("\n🔍 Working Memory Demo")
    print("-" * 30)
    
    # Create working memory with TTL (time-to-live)
    working_memory = WorkingMemory(
        config={
            "ttl": 600  # 10 minutes
        }
    )
    
    # Add items to working memory
    working_items = [
        ("current_project", {"name": "AI Assistant", "status": "active", "deadline": "2024-12-31"}, 0.8),
        ("user_preferences", {"theme": "dark", "language": "en", "notifications": True}, 0.6),
        ("session_data", {"user_id": "user_123", "start_time": datetime.now().isoformat()}, 0.7),
        ("task_queue", ["process_data", "send_notification", "update_status"], 0.9)
    ]
    
    for key, value, importance in working_items:
        working_memory.add_item(key, value, importance)
        print(f"✅ Added to working memory: {key}")
    
    # Retrieve items from working memory
    project_info = working_memory.get_item("current_project")
    if project_info:
        print(f"\nRetrieved project info: {project_info}")
    
    user_prefs = working_memory.get_item("user_preferences")
    if user_prefs:
        print(f"Retrieved user prefs: {user_prefs}")
    
    # Working memory has TTL - items expire automatically
    print(f"Working memory TTL: {working_memory.ttl} seconds")
    print("Items in working memory automatically expire after TTL")
    
    return working_memory

async def demo_memory_manager():
    """Demo the main memory manager that combines all memory types"""
    print("\n🔍 Memory Manager Demo (Combined Memory System)")
    print("-" * 30)
    
    # Create a comprehensive memory configuration
    memory_config = {
        "conversation": {
            "max_turns": 100,
            "compression_enabled": True
        },
        "episodic": {
            "episode_tags": ["task", "session", "interaction", "project", "bug", "meeting"]
        },
        "semantic": {
            "relevance_threshold": 0.5,
            "embedding_dim": 384
        },
        "working": {
            "ttl": 1200  # 20 minutes
        }
    }
    
    # Create memory manager with all memory types
    memory_manager = MemoryManager(config=memory_config)
    
    from cynergy.memory.memory_manager import MemoryType
    
    print("Memory manager created with all memory types:")
    print(f"  • Conversation: Max {memory_manager.memories[MemoryType.CONVERSATION].max_turns} turns")
    print(f"  • Episodic: Tags {memory_manager.memories[MemoryType.EPISODIC].episode_tags}")
    print(f"  • Semantic: Relevance threshold {memory_manager.memories[MemoryType.SEMANTIC].relevance_threshold}")
    print(f"  • Working: TTL {memory_manager.memories[MemoryType.WORKING].ttl}s")
    
    # Add content to different memory types
    from cynergy.core.agent import Message
    
    # Add to conversation memory
    memory_manager.add_message(Message(role="user", content="What was our project goal again?"))
    memory_manager.add_message(Message(role="assistant", content="Our goal is to build an AI assistant with advanced memory capabilities."))
    
    # Add to episodic memory
    memory_manager.add_episode("Discussed project goals with stakeholders", ["meeting", "planning"], 0.9)
    
    # Add to semantic memory
    memory_manager.add_knowledge("AI assistants can use multiple memory types to improve performance", ["ai", "memory", "performance"], None)
    
    # Add to working memory
    memory_manager.set_working_item("current_task", "Implement memory features", 0.8)
    
    print("\nAdded items to different memory types:")
    print(f"  • Conversation: {len(memory_manager.memories[MemoryType.CONVERSATION].chunks)} messages")
    print(f"  • Episodic: {len(memory_manager.memories[MemoryType.EPISODIC].chunks)} episodes")
    print(f"  • Semantic: {len(memory_manager.memories[MemoryType.SEMANTIC].chunks)} knowledge items")
    print(f"  • Working: {len(memory_manager.memories[MemoryType.WORKING].chunks)} items")
    
    # Retrieve from different memory types
    context_messages = memory_manager.get_context_messages()
    print(f"\nRetrieved {len(context_messages)} context messages from conversation memory")
    
    episode_results = memory_manager.search_episodes(["planning"])
    print(f"Found {len(episode_results)} planning-related episodes")
    
    knowledge_results = memory_manager.search_knowledge("memory capabilities", top_k=2)
    print(f"Found {len(knowledge_results)} knowledge items about memory capabilities")
    
    current_task = memory_manager.get_working_item("current_task")
    print(f"Current task from working memory: {current_task}")
    
    return memory_manager

async def demo_memory_with_agent():
    """Demo how memory integrates with agents"""
    print("\n🔗 Memory Integration with Agents")
    print("-" * 30)
    
    # Create a memory manager
    memory_manager = MemoryManager(config={
        "conversation": {"max_turns": 50, "compression_enabled": True},
        "working": {"ttl": 600}
    })
    
    # Create an agent with enhanced memory
    mock_model = create_mock_model()
    agent = Agent(
        name="MemoryEnhancedAgent",
        model=mock_model,  # Using mock model for demo
        memory=memory_manager,
        system_prompt="You are an AI assistant with enhanced memory capabilities. Remember important information across conversations."
    )
    
    print(f"Agent '{agent.name}' created with enhanced memory")
    print(f"Memory types available: {list(agent.memory.memories.keys())}")
    
    # Simulate agent interactions that use memory
    print("\nSimulating agent interactions with memory:")
    
    # Add context to working memory
    agent.memory.set_working_item("user_context", {
        "name": "Developer",
        "interests": ["AI", "Python", "Automation"],
        "skill_level": "intermediate"
    }, importance=0.8)
    
    print("  • Added user context to working memory")
    
    # Add project information to episodic memory
    agent.memory.add_episode("User wants to build an AI agent with Cynergy", ["task", "ai", "cynergy"], 0.9)
    print("  • Added project goal to episodic memory")
    
    # Add some conversation history
    from cynergy.core.agent import Message
    
    agent.memory.add_message(Message(role="system", content="You are an AI assistant with enhanced memory capabilities."))
    agent.memory.add_message(Message(role="user", content="How do I build an AI agent using Cynergy?"))
    agent.memory.add_message(Message(role="assistant", content="You can build an AI agent with Cynergy by creating an Agent instance with a model, memory, and tools."))
    
    print("  • Added conversation history to memory")
    
    # Retrieve memory information
    current_context = agent.memory.get_context_messages()
    print(f"  • Retrieved {len(current_context)} context messages")
    
    user_context = agent.memory.get_working_item("user_context")
    print(f"  • Retrieved user context: {user_context['interests'] if user_context else 'None'}")
    
    project_info = agent.memory.search_episodes(["task"])
    print(f"  • Retrieved {len(project_info)} task-related episodes")
    
    print(f"\nAgent state: {agent.state}")
    print(f"Agent has memory and can recall information across interactions")
    
    return agent

async def main():
    """Main function demonstrating all memory capabilities"""
    print("🚀 Cynergy Memory Management Demo")
    print("=" * 50)
    print("This demo shows the advanced memory management features in Cynergy\n")
    
    # Demo individual memory types
    conv_memory = await demo_conversation_memory()
    episodic_memory = await demo_episodic_memory()
    semantic_memory = await demo_semantic_memory()
    working_memory = await demo_working_memory()
    
    # Demo combined memory manager
    memory_manager = await demo_memory_manager()
    
    # Demo memory integration with agents
    agent_with_memory = await demo_memory_with_agent()
    
    print("\n" + "=" * 50)
    print("📋 Memory Management Summary:")
    print("• Conversation Memory: Stores dialogue history with compression")
    print("• Episodic Memory: Stores specific events/experiences with tags")
    print("• Semantic Memory: Stores knowledge for similarity search")
    print("• Working Memory: Short-term storage with TTL")
    print("• Memory Manager: Unified interface for all memory types")
    
    print("\n💡 Memory Best Practices:")
    print("• Use conversation memory for dialogue context")
    print("• Store important events in episodic memory with relevant tags")
    print("• Add domain knowledge to semantic memory")
    print("• Use working memory for temporary session data")
    print("• Configure appropriate limits to manage memory usage")
    print("• Regularly clear or compress memory as needed")
    
    print("\n🔗 Memory Configuration Options:")
    print("• Max turns for conversation memory")
    print("• Compression to handle long conversations")
    print("• TTL for working memory items")
    print("• Relevance thresholds for semantic search")
    print("• Custom tags for episodic memories")

if __name__ == "__main__":
    asyncio.run(main())