import traceback
from datetime import datetime
from typing import List

from memory.embedding.embedder import Embedder
from memory.vector_store.faiss_store import FAISSStore


class MemoryManager:
    """
    Institutional-Grade Memory Manager (RAG Core)

    Responsibilities:
    - Embedding generation
    - Semantic retrieval
    - Context construction (LLM-ready)
    - Persistent memory storage

    Guarantees:
    - Fault-tolerant
    - HPC-safe
    - Deterministic
    - Scalable
    """

    def __init__(
        self,
        embedder: Embedder = None,
        store: FAISSStore = None,
        top_k: int = 5,
        max_context_chars: int = 2000
    ):
        self.embedder = embedder if embedder else Embedder()
        self.store = store if store else FAISSStore()

        self.top_k = top_k
        self.max_context_chars = max_context_chars

        self._log_init()

    # ==================================================
    # LOGGING
    # ==================================================
    def _log_init(self):
        print("\n========== MEMORY MANAGER INIT ==========")
        print(f"[TOP_K] {self.top_k}")
        print(f"[MAX_CONTEXT_CHARS] {self.max_context_chars}")
        print(f"[STORE SIZE] {self.store.size()}")

    def _log(self, msg: str):
        print(msg)

    # ==================================================
    # STORE MEMORY
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
            self.store.add(vector, text)

        except Exception:
            self._log("[MEMORY ERROR] Store failed")
            traceback.print_exc()

    # ==================================================
    # RETRIEVE MEMORY
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

            results = self.store.search(vector, self.top_k)

            self._log(f"[MEMORY] Retrieved {len(results)} items")

            return results

        except Exception:
            self._log("[MEMORY ERROR] Retrieval failed")
            traceback.print_exc()
            return []

    # ==================================================
    # CONTEXT BUILDING (CRITICAL RAG STEP)
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
    # PROMPT AUGMENTATION (RAG CORE)
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

            if context:
                return f"{context}\n\nUser Query:\n{query}"
            else:
                return query

        except Exception:
            self._log("[MEMORY ERROR] Prompt augmentation failed")
            traceback.print_exc()
            return query

    # ==================================================
    # HEALTH CHECK
    # ==================================================
    def health_check(self) -> bool:
        try:
            test = "memory system test"
            vec = self.embedder.encode_one(test)

            return vec is not None and self.store.health_check()

        except Exception:
            return False
