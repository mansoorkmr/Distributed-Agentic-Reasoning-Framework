from __future__ import annotations

import json
import traceback
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List

# --- Original Imports (Retained) ---
from memory.embedding.embedder import Embedder
from memory.vector_store.faiss_store import FAISSStore

# --- New Imports ---
from memory.working_memory import WorkingMemory
from memory.episodic_memory import EpisodicMemory
from memory.semantic_memory import SemanticMemory
from memory.memory_policy import MemoryPolicy
from memory.memory_metrics import MemoryMetrics
from memory.memory_item import MemoryItem


@dataclass(slots=True)
class MemoryManager:
    """
    Institutional-Grade Memory Manager (RAG Core & Modular Memory)

    Responsibilities:
    - Embedding generation & semantic retrieval
    - Context construction (LLM-ready)
    - Working, Episodic, and Semantic memory handling
    - Persistent memory storage
    """

    # --- New Modular Memory Fields ---
    working: WorkingMemory = field(default_factory=WorkingMemory)
    episodic: EpisodicMemory = field(default_factory=EpisodicMemory)
    semantic: SemanticMemory = field(default_factory=SemanticMemory)
    policy: MemoryPolicy = field(default_factory=MemoryPolicy)
    metrics: MemoryMetrics = field(default_factory=MemoryMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    # --- Original RAG Fields ---
    embedder: Embedder = field(default_factory=Embedder)
    faiss_store: FAISSStore = field(default_factory=FAISSStore)  # Renamed from 'store' to prevent method shadowing
    top_k: int = 5
    max_context_chars: int = 2000

    def __post_init__(self):
        """Replaces the original __init__ logic for dataclasses"""
        self._log_init()

    # ==================================================
    # LOGGING (Original)
    # ==================================================
    def _log_init(self):
        print("\n========== MEMORY MANAGER INIT ==========")
        print(f"[TOP_K] {self.top_k}")
        print(f"[MAX_CONTEXT_CHARS] {self.max_context_chars}")
        print(f"[STORE SIZE] {self.faiss_store.size()}")

    def _log(self, msg: str):
        print(msg)

    # ==================================================
    # STORE MEMORY (Original)
    # ==================================================
    def store(self, query: str, response: str):
        """
        Store interaction in persistent memory
        """
        try:
            if not query or not response:
                self._log("[MEMORY WARNING] Empty query/response, skipping store")
                return

            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query.strip(),
                "response": response.strip()
            }

            text = f"Query: {entry['query']}\nResponse: {entry['response']}"

            vector = self.embedder.encode_one(text)

            if vector is None:
                self._log("[MEMORY ERROR] Embedding failed, skipping store")
                return

            self._log("[MEMORY] Storing new interaction")
            self.faiss_store.add(vector, text)

        except Exception:
            self._log("[MEMORY ERROR] Store failed")
            traceback.print_exc()

    # ==================================================
    # RETRIEVE MEMORY (Original)
    # ==================================================
    def retrieve(self, query: str) -> List[str]:
        """
        Retrieve semantically similar past interactions
        """
        try:
            if not query or len(query.strip()) == 0:
                return []

            vector = self.embedder.encode_one(query)

            if vector is None:
                return []

            results = self.faiss_store.search(vector, self.top_k)

            self._log(f"[MEMORY] Retrieved {len(results)} items")

            return results

        except Exception:
            self._log("[MEMORY ERROR] Retrieval failed")
            traceback.print_exc()
            return []

    # ==================================================
    # CONTEXT BUILDING (Original)
    # ==================================================
    def build_context(self, query: str) -> str:
        """
        Build structured context for LLM
        """
        try:
            retrieved = self.retrieve(query)

            if not retrieved:
                return ""

            context_blocks = []
            total_length = 0

            for item in retrieved:
                if not item:
                    continue

                cleaned = item.strip().replace("\n", " ")
                block = f"- {cleaned}\n"

                if total_length + len(block) > self.max_context_chars:
                    break

                context_blocks.append(block)
                total_length += len(block)

            if not context_blocks:
                return ""

            context = "Relevant past knowledge:\n\n" + "".join(context_blocks)

            return context.strip()

        except Exception:
            self._log("[MEMORY ERROR] Context build failed")
            traceback.print_exc()
            return ""

    # ==================================================
    # PROMPT AUGMENTATION (Original)
    # ==================================================
    def augment_prompt(self, query: str) -> str:
        """
        Combine memory + user query
        """
        try:
            context = self.build_context(query)

            # DEBUG (can be disabled later)
            if context:
                self._log("\n[MEMORY CONTEXT]")
                self._log(context)
                return f"{context}\n\nUser Query:\n{query}"
            else:
                return query

        except Exception:
            self._log("[MEMORY ERROR] Prompt augmentation failed")
            traceback.print_exc()
            return query

    # ==================================================
    # HEALTH CHECK (Original)
    # ==================================================
    def health_check(self) -> bool:
        try:
            test = "memory system test"
            vec = self.embedder.encode_one(test)

            return vec is not None and self.faiss_store.health_check()

        except Exception:
            return False

    # ==================================================
    # NEW MODULAR MEMORY METHODS
    # ==================================================
    def remember(self, key: str, value: Any) -> None:
        self.semantic.remember(key, value)
        self.metrics.record_insertion()

    def recall(self, key: str) -> Any:
        value = self.semantic.recall(key)
        if value is None:
            self.metrics.record_miss()
        else:
            self.metrics.record_hit()
        return value

    def set_working(self, key: str, value: Any) -> None:
        self.working.set(key, value)

    def get_working(self, key: str) -> Any:
        return self.working.get(key)

    def remember_episode(self, key: str, value: Any) -> None:
        self.episodic.add(
            MemoryItem(
                key=key,
                value=value,
            )
        )

    def forget(self, key: str) -> None:
        self.semantic.forget(key)
        self.metrics.record_removal()

    def clear(self) -> None:
        self.working.clear()
        self.semantic.clear()
        self.episodic.clear()

    def statistics(self) -> Dict[str, Any]:
        return self.metrics.to_dict()

    # ==================================================
    # SERIALIZATION & REPRESENTATION
    # ==================================================
    def to_dict(self):
        return {
            "working": self.working.to_dict(),
            "episodic": self.episodic.to_dict(),
            "semantic": self.semantic.to_dict(),
            "policy": self.policy.to_dict(),
            "metrics": self.metrics.to_dict(),
            "metadata": self.metadata,
            "version": self.version,
        }

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            indent=4,
            sort_keys=True,
        )

    def __str__(self):
        return (
            "MemoryManager("
            f"{self.semantic.count()} facts, "
            f"{self.episodic.count()} episodes)"
        )

    def __repr__(self):
        return (
            "<MemoryManager "
            f"facts={self.semantic.count()} "
            f"episodes={self.episodic.count()}>"
        )