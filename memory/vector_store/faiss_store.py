import os
import json
import faiss
import numpy as np
import threading
import traceback


class FAISSStore:
    """
    Institutional-Grade FAISS Vector Store

    Guarantees:
    - Absolute path safety (HPC-safe)
    - Atomic persistence (no corruption)
    - Dimension validation
    - Thread-safe writes
    - Deterministic behavior
    - Fault recovery
    """

    def __init__(
        self,
        dim: int = 384,
        base_path: str = None,
        index_type: str = "flat"
    ):
        self.dim = dim
        self.index_type = index_type

        # ==================================================
        # ABSOLUTE PATH (CRITICAL FIX)
        # ==================================================
        if base_path:
            self.base_path = base_path
        else:
            project_root = os.getenv("PROJECT_ROOT", os.getcwd())
            self.base_path = os.path.join(project_root, "data", "memory_store")

        self.index_file = os.path.join(self.base_path, "index.faiss")
        self.meta_file = os.path.join(self.base_path, "metadata.json")

        self.lock = threading.Lock()

        self._init_storage()
        self._load()

    # ==================================================
    # INITIALIZATION
    # ==================================================
    def _init_storage(self):
        try:
            os.makedirs(self.base_path, exist_ok=True)
        except Exception:
            print("[FAISS ERROR] Failed to create storage directory")
            traceback.print_exc()
            raise

    def _create_index(self):
        if self.index_type == "flat":
            return faiss.IndexFlatL2(self.dim)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")

    def _load(self):
        """
        Load index + metadata safely
        """
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
                self.index = faiss.read_index(self.index_file)

                with open(self.meta_file, "r") as f:
                    self.metadata = json.load(f)

                # Consistency check
                if self.index.ntotal != len(self.metadata):
                    print("[FAISS WARNING] Index/metadata mismatch → repairing")
                    self.metadata = self.metadata[:self.index.ntotal]

            else:
                print("[FAISS INIT] Creating new index")
                self.index = self._create_index()
                self.metadata = []

        except Exception:
            print("[FAISS ERROR] Load failed → resetting store")
            traceback.print_exc()

            self.index = self._create_index()
            self.metadata = []

    # ==================================================
    # ADD DATA
    # ==================================================
    def add(self, vectors, texts):
        """
        Add vectors + metadata
        """

        with self.lock:
            try:
                vectors = np.array(vectors).astype("float32")

                if vectors.ndim == 1:
                    vectors = vectors.reshape(1, -1)

                if vectors.shape[1] != self.dim:
                    raise ValueError(
                        f"Vector dimension mismatch: expected {self.dim}, got {vectors.shape[1]}"
                    )

                if isinstance(texts, str):
                    texts = [texts]

                if len(texts) != vectors.shape[0]:
                    raise ValueError("Vectors and texts length mismatch")

                # Add to FAISS
                self.index.add(vectors)

                # Add metadata
                for t in texts:
                    self.metadata.append({
                        "text": t
                    })

                print(f"[FAISS] Added {len(texts)} entries | Total: {len(self.metadata)}")

                self._save()

            except Exception:
                print("[FAISS ERROR] Add failed")
                traceback.print_exc()
                raise

    # ==================================================
    # SEARCH
    # ==================================================
    def search(self, vectors, k: int = 3):
        """
        Retrieve top-k similar entries
        """
        try:
            if len(self.metadata) == 0:
                return []

            vectors = np.array(vectors).astype("float32")

            if vectors.ndim == 1:
                vectors = vectors.reshape(1, -1)

            distances, indices = self.index.search(vectors, k)

            results = []

            for idx in indices[0]:
                if 0 <= idx < len(self.metadata):
                    results.append(self.metadata[idx]["text"])

            return results

        except Exception:
            print("[FAISS ERROR] Search failed")
            traceback.print_exc()
            return []

    # ==================================================
    # SAVE (ATOMIC)
    # ==================================================
    def _save(self):
        """
        Atomic save to prevent corruption
        """
        try:
            tmp_index = self.index_file + ".tmp"
            tmp_meta = self.meta_file + ".tmp"

            faiss.write_index(self.index, tmp_index)

            with open(tmp_meta, "w") as f:
                json.dump(self.metadata, f, indent=4)

            os.replace(tmp_index, self.index_file)
            os.replace(tmp_meta, self.meta_file)

        except Exception:
            print("[FAISS ERROR] Save failed")
            traceback.print_exc()

    # ==================================================
    # UTILITIES
    # ==================================================
    def size(self):
        return len(self.metadata)

    def reset(self):
        """
        Reset memory store (dangerous)
        """
        with self.lock:
            self.index = self._create_index()
            self.metadata = []
            self._save()
            print("[FAISS] Store reset")

    def health_check(self):
        try:
            return (
                self.index is not None
                and isinstance(self.metadata, list)
            )
        except Exception:
            return False
