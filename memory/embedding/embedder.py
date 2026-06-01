import os
import torch
import traceback
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """
    Institutional-Grade Embedding Engine

    Features:
    - Deterministic embeddings
    - GPU/CPU fallback
    - Batch processing support
    - Normalized vectors (FAISS-ready)
    - Fault-tolerant
    - HPC-safe (no memory spikes)
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = None,
        batch_size: int = 32
    ):
        self.model_name = model_name
        self.batch_size = batch_size

        # --------------------------------------------------
        # DEVICE DETECTION (SAFE)
        # --------------------------------------------------
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self._log_header()

        # --------------------------------------------------
        # LOAD MODEL (SAFE)
        # --------------------------------------------------
        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device
            )

        except RuntimeError as e:
            self._log("[EMBEDDER WARNING] GPU load failed → switching to CPU")
            self.device = "cpu"
            self.model = SentenceTransformer(self.model_name, device="cpu")

        except Exception as e:
            self._fatal("Failed to load embedding model", e)

        # --------------------------------------------------
        # FORCE EVAL MODE (STABILITY)
        # --------------------------------------------------
        try:
            self.model.eval()
        except Exception:
            pass

    # ==================================================
    # LOGGING
    # ==================================================
    def _log_header(self):
        print("\n========== EMBEDDER INIT ==========")
        print(f"[MODEL] {self.model_name}")
        print(f"[DEVICE] {self.device}")
        print(f"[BATCH SIZE] {self.batch_size}")

    def _log(self, msg):
        print(msg)

    def _fatal(self, msg, err):
        print(f"\n[FATAL EMBEDDER ERROR] {msg}")
        traceback.print_exc()
        raise RuntimeError(msg)

    # ==================================================
    # INPUT VALIDATION
    # ==================================================
    def _validate_input(self, texts):
        if texts is None:
            raise ValueError("Input text is None")

        if isinstance(texts, str):
            return [texts]

        if isinstance(texts, list):
            # ensure all elements are strings
            cleaned = []
            for t in texts:
                if t is None:
                    continue
                if not isinstance(t, str):
                    t = str(t)
                t = t.strip()
                if len(t) > 0:
                    cleaned.append(t)

            if len(cleaned) == 0:
                raise ValueError("No valid text provided")

            return cleaned

        raise TypeError("Input must be string or list of strings")

    # ==================================================
    # NORMALIZATION (CRITICAL FOR FAISS)
    # ==================================================
    def _normalize(self, vectors):
        norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10
        return vectors / norms

    # ==================================================
    # ENCODING (CORE FUNCTION)
    # ==================================================
    def encode(self, texts):
        """
        Converts text(s) → normalized embeddings

        Returns:
            np.ndarray shape (n, dim)
        """

        try:
            texts = self._validate_input(texts)

            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            embeddings = embeddings.astype("float32")

            # --------------------------------------------------
            # NORMALIZE (VERY IMPORTANT)
            # --------------------------------------------------
            embeddings = self._normalize(embeddings)

            return embeddings

        except RuntimeError as e:
            # GPU failure fallback
            if "CUDA" in str(e):
                self._log("[EMBEDDER WARNING] CUDA error → switching to CPU")

                self.device = "cpu"
                self.model = SentenceTransformer(self.model_name, device="cpu")

                return self.encode(texts)

            raise

        except Exception as e:
            self._fatal("Encoding failed", e)

    # ==================================================
    # SINGLE VECTOR HELPER
    # ==================================================
    def encode_one(self, text):
        """
        Returns single embedding vector (1D)
        """
        return self.encode(text)[0]

    # ==================================================
    # HEALTH CHECK
    # ==================================================
    def health_check(self):
        try:
            vec = self.encode("test embedding")
            return vec is not None and len(vec.shape) == 2
        except Exception:
            return False
