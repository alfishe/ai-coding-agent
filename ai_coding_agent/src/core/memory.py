from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Memory(BaseModel):
    """Represents a memory item in the system."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    content: str
    corpus_names: Set[str] = Field(default_factory=set)
    tags: Set[str] = Field(default_factory=set)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_triggered: bool = False


class MemoryManager:
    """Manages the storage and retrieval of memories."""
    
    def __init__(self):
        self._memories: Dict[UUID, Memory] = {}
    
    def create_memory(
        self,
        title: str,
        content: str,
        corpus_names: Optional[Set[str]] = None,
        tags: Optional[Set[str]] = None,
        user_triggered: bool = False
    ) -> Memory:
        """Create a new memory."""
        memory = Memory(
            title=title,
            content=content,
            corpus_names=corpus_names or set(),
            tags=tags or set(),
            user_triggered=user_triggered
        )
        self._memories[memory.id] = memory
        return memory
    
    def update_memory(
        self,
        memory_id: UUID,
        title: Optional[str] = None,
        content: Optional[str] = None,
        corpus_names: Optional[Set[str]] = None,
        tags: Optional[Set[str]] = None
    ) -> Optional[Memory]:
        """Update an existing memory."""
        if memory_id not in self._memories:
            return None
        
        memory = self._memories[memory_id]
        if title is not None:
            memory.title = title
        if content is not None:
            memory.content = content
        if corpus_names is not None:
            memory.corpus_names = corpus_names
        if tags is not None:
            memory.tags = tags
        
        memory.updated_at = datetime.utcnow()
        return memory
    
    def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory."""
        if memory_id not in self._memories:
            return False
        
        del self._memories[memory_id]
        return True
    
    def get_memory(self, memory_id: UUID) -> Optional[Memory]:
        """Get a memory by ID."""
        return self._memories.get(memory_id)
    
    def search_memories(
        self,
        query: Optional[str] = None,
        corpus_names: Optional[Set[str]] = None,
        tags: Optional[Set[str]] = None
    ) -> List[Memory]:
        """Search memories by various criteria."""
        results = list(self._memories.values())
        
        if query:
            query = query.lower()
            results = [
                m for m in results
                if query in m.title.lower() or query in m.content.lower()
            ]
        
        if corpus_names:
            results = [
                m for m in results
                if corpus_names.issubset(m.corpus_names)
            ]
        
        if tags:
            results = [
                m for m in results
                if tags.issubset(m.tags)
            ]
        
        return results 