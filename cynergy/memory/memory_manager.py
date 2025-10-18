"""Enhanced memory management for Cynergy agents"""
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
import uuid
from enum import Enum

from cynergy.core.agent import Message


class MemoryType(Enum):
    CONVERSATION = "conversation"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"


@dataclass
class MemoryChunk:
    """A chunk of memory with metadata"""
    id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 1.0  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None  # For semantic search


class BaseMemory:
    """Base class for different memory types"""
    def __init__(self, memory_type: MemoryType, config: Optional[Dict[str, Any]] = None):
        self.memory_type = memory_type
        self.config = config or {}
        self.chunks: List[MemoryChunk] = []
        self.max_size = self.config.get("max_size", 1000)  # Max chunks to keep
        self.compression_threshold = self.config.get("compression_threshold", 0.8)  # Compress when 80% full

    def add_chunk(self, chunk: MemoryChunk):
        """Add a chunk to memory"""
        self.chunks.append(chunk)
        self._enforce_limits()

    def get_relevant_chunks(self, query: str, top_k: int = 5) -> List[MemoryChunk]:
        """Get relevant chunks based on the query"""
        # Default implementation: simple keyword matching
        relevant_chunks = []
        query_lower = query.lower()
        
        for chunk in self.chunks:
            if query_lower in chunk.content.lower():
                relevant_chunks.append(chunk)
        
        # Sort by importance and recency
        relevant_chunks.sort(key=lambda x: (x.importance, x.timestamp.timestamp()), reverse=True)
        return relevant_chunks[:top_k]

    def _enforce_limits(self):
        """Enforce memory limits by compressing or removing chunks"""
        while len(self.chunks) > self.max_size:
            # Remove the least important and oldest chunks
            self.chunks.sort(key=lambda x: (x.importance, x.timestamp.timestamp()))
            self.chunks.pop(0)

    def clear(self):
        """Clear all memory"""
        self.chunks = []


class ConversationMemory(BaseMemory):
    """Basic conversation memory with compression"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(MemoryType.CONVERSATION, config)
        self.max_turns = self.config.get("max_turns", 50)
        self.compression_enabled = self.config.get("compression_enabled", True)

    def add_message(self, message: Message):
        """Add a message to conversation memory"""
        chunk = MemoryChunk(
            id=str(uuid.uuid4()),
            content=message.content,
            timestamp=message.timestamp,
            importance=self._calculate_importance(message),
            metadata=message.metadata
        )
        self.add_chunk(chunk)

    def _calculate_importance(self, message: Message) -> float:
        """Calculate importance of a message (0.0 to 1.0)"""
        # System messages are more important
        if message.role == "system":
            return 1.0
        
        # Tool results might be less important than user/assistant messages
        if message.role == "tool":
            return 0.3
        
        # User and assistant messages have medium to high importance
        return 0.7

    def get_context_messages(self) -> List[Message]:
        """Get messages for context, with compression applied if needed"""
        if len(self.chunks) > self.max_turns and self.compression_enabled:
            # Apply compression by keeping important chunks
            important_chunks = [c for c in self.chunks if c.importance >= 0.7]
            other_chunks = [c for c in self.chunks if c.importance < 0.7]
            
            # Keep all important chunks, and keep recent non-important chunks
            other_chunks = sorted(other_chunks, key=lambda x: x.timestamp, reverse=True)[:self.max_turns - len(important_chunks)]
            
            selected_chunks = important_chunks + other_chunks
            selected_chunks.sort(key=lambda x: x.timestamp)
        else:
            selected_chunks = sorted(self.chunks[-self.max_turns:], key=lambda x: x.timestamp)

        # Convert back to Messages
        messages = []
        for chunk in selected_chunks:
            messages.append(Message(
                role=chunk.metadata.get("role", "assistant"),
                content=chunk.content,
                timestamp=chunk.timestamp,
                metadata=chunk.metadata
            ))
        return messages


class EpisodicMemory(BaseMemory):
    """Memory for storing episodic experiences"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(MemoryType.EPISODIC, config)
        self.episode_tags = self.config.get("episode_tags", ["task", "session", "interaction"])

    def add_episode(self, content: str, tags: List[str] = None, importance: float = 0.5):
        """Add an episodic memory"""
        chunk = MemoryChunk(
            id=str(uuid.uuid4()),
            content=content,
            importance=importance,
            tags=tags or []
        )
        self.add_chunk(chunk)

    def get_episodes_by_tags(self, tags: List[str]) -> List[MemoryChunk]:
        """Get episodes that match any of the provided tags"""
        result = []
        for chunk in self.chunks:
            if any(tag in chunk.tags for tag in tags):
                result.append(chunk)
        return result


class SemanticMemory(BaseMemory):
    """Memory for semantic knowledge with retrieval capabilities"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(MemoryType.SEMANTIC, config)
        self.embedding_dim = self.config.get("embedding_dim", 384)  # Default for sentence transformers
        self.relevance_threshold = self.config.get("relevance_threshold", 0.5)

    def add_knowledge(self, content: str, tags: List[str] = None, embedding: List[float] = None):
        """Add semantic knowledge to memory"""
        chunk = MemoryChunk(
            id=str(uuid.uuid4()),
            content=content,
            importance=0.8,  # Semantic knowledge is generally important
            tags=tags or [],
            embedding=embedding
        )
        self.add_chunk(chunk)

    def search_similar(self, query: str, top_k: int = 5) -> List[MemoryChunk]:
        """Search for similar knowledge using semantic similarity"""
        # For now, we'll implement a simple semantic search using keyword matching
        # In a real implementation, this would use vector embeddings
        
        # For now, we'll just use the base get_relevant_chunks method
        # Future implementation could use actual semantic search
        return self.get_relevant_chunks(query, top_k)


class WorkingMemory(BaseMemory):
    """Short-term working memory for current task"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(MemoryType.WORKING, config)
        self.ttl = self.config.get("ttl", 300)  # Time-to-live in seconds

    def add_item(self, key: str, value: Any, importance: float = 0.5):
        """Add an item to working memory"""
        chunk = MemoryChunk(
            id=key,
            content=json.dumps(value),
            importance=importance,
            metadata={"added_at": datetime.now().isoformat()}
        )
        self.add_chunk(chunk)

    def get_item(self, key: str) -> Optional[Any]:
        """Get an item from working memory"""
        for chunk in self.chunks:
            if chunk.id == key:
                try:
                    return json.loads(chunk.content)
                except json.JSONDecodeError:
                    return chunk.content
        return None

    def _enforce_limits(self):
        """Remove expired items"""
        current_time = datetime.now()
        # Remove items that are older than TTL
        self.chunks = [
            chunk for chunk in self.chunks
            if (current_time - datetime.fromisoformat(chunk.metadata["added_at"])).seconds < self.ttl
        ]


class MemoryManager:
    """Main memory manager that combines all memory types"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.memories: Dict[MemoryType, BaseMemory] = {
            MemoryType.CONVERSATION: ConversationMemory(self.config.get("conversation", {})),
            MemoryType.EPISODIC: EpisodicMemory(self.config.get("episodic", {})),
            MemoryType.SEMANTIC: SemanticMemory(self.config.get("semantic", {})),
            MemoryType.WORKING: WorkingMemory(self.config.get("working", {})),
        }

    def add_message(self, message: Message):
        """Add a message to conversation memory"""
        self.memories[MemoryType.CONVERSATION].add_message(message)

    def add_episode(self, content: str, tags: List[str] = None, importance: float = 0.5):
        """Add an episodic memory"""
        self.memories[MemoryType.EPISODIC].add_episode(content, tags, importance)

    def add_knowledge(self, content: str, tags: List[str] = None, embedding: List[float] = None):
        """Add semantic knowledge"""
        self.memories[MemoryType.SEMANTIC].add_knowledge(content, tags, embedding)

    def set_working_item(self, key: str, value: Any, importance: float = 0.5):
        """Add an item to working memory"""
        self.memories[MemoryType.WORKING].add_item(key, value, importance)

    def get_working_item(self, key: str) -> Optional[Any]:
        """Get an item from working memory"""
        return self.memories[MemoryType.WORKING].get_item(key)

    def get_context_messages(self) -> List[Message]:
        """Get context messages from conversation memory"""
        return self.memories[MemoryType.CONVERSATION].get_context_messages()

    def search_episodes(self, tags: List[str]) -> List[MemoryChunk]:
        """Search episodic memory by tags"""
        return self.memories[MemoryType.EPISODIC].get_episodes_by_tags(tags)

    def search_knowledge(self, query: str, top_k: int = 5) -> List[MemoryChunk]:
        """Search semantic memory"""
        return self.memories[MemoryType.SEMANTIC].search_similar(query, top_k)

    def clear_all(self):
        """Clear all memories"""
        for memory in self.memories.values():
            memory.clear()