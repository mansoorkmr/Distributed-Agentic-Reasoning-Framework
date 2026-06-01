"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Tokenizer Loader Infrastructure

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade tokenizer loading and orchestration
    infrastructure for:

        - institutional transformer systems
        - distributed AI runtimes
        - scalable preprocessing pipelines
        - multi-agent reasoning systems
        - HPC-aware inference pipelines
        - production-grade tokenization
        - deterministic NLP execution
        - large-scale language modeling

Core Responsibilities:
    - tokenizer loading
    - tokenizer validation
    - distributed-safe initialization
    - special token management
    - tokenizer metadata orchestration
    - deterministic preprocessing
    - tokenizer runtime observability
    - institutional reproducibility

Design Principles:
    - deterministic
    - fault-tolerant
    - distributed-safe
    - production-grade
    - institutionally reproducible
    - scalable
    - memory efficient
    - future extensible

Supported Features:
    - AutoTokenizer loading
    - fast tokenizer support
    - tokenizer validation
    - pad token correction
    - special token orchestration
    - tokenizer metadata export
    - distributed-safe loading
    - runtime telemetry
"""

import json
import os
import traceback
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

from transformers import (
    AutoTokenizer,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

from infrastructure.logging.structured_logger import (
    get_logger,
)


class TokenizerLoader:
    """
    Institutional-grade tokenizer loader.

    Handles:
        - tokenizer initialization
        - tokenizer validation
        - distributed-safe loading
        - preprocessing orchestration
        - runtime observability
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        model_name: str,
        use_fast: bool = True,
        trust_remote_code: bool = False,
        padding_side: str = "right",
        truncation_side: str = "right",
        force_pad_token: bool = True,
    ):

        self.model_name = model_name

        self.use_fast = use_fast

        self.trust_remote_code = (
            trust_remote_code
        )

        self.padding_side = (
            padding_side
        )

        self.truncation_side = (
            truncation_side
        )

        self.force_pad_token = (
            force_pad_token
        )

        self.logger = get_logger(
            name="TokenizerLoader",
            log_dir="logs/llm",
        )

        # ========================================================
        # TOKENIZER STATE
        # ========================================================

        self.tokenizer = None

        self.loaded = False

        self.created_at = (
            datetime.utcnow().isoformat()
        )

        self.logger.info(
            f"TokenizerLoader initialized | "
            f"Model={self.model_name}"
        )

    # ============================================================
    # VALIDATION
    # ============================================================

    def validate_configuration(
        self,
    ):
        """
        Validate tokenizer configuration safely.
        """

        valid_sides = {

            "left",

            "right",
        }

        if (
            self.padding_side
            not in valid_sides
        ):

            raise ValueError(
                f"Invalid padding_side: "
                f"{self.padding_side}"
            )

        if (
            self.truncation_side
            not in valid_sides
        ):

            raise ValueError(
                f"Invalid truncation_side: "
                f"{self.truncation_side}"
            )

    # ============================================================
    # LOAD TOKENIZER
    # ============================================================

    def load_tokenizer(
        self,
    ) -> (
        PreTrainedTokenizer
        | PreTrainedTokenizerFast
    ):
        """
        Load institutional tokenizer safely.
        """

        try:

            self.validate_configuration()

            self.logger.info(
                f"Loading tokenizer | "
                f"Model={self.model_name}"
            )

            tokenizer = (
                AutoTokenizer
                .from_pretrained(

                    self.model_name,

                    use_fast=self.use_fast,

                    trust_remote_code=(
                        self.trust_remote_code
                    ),
                )
            )

            # ----------------------------------------------------
            # TOKENIZER SIDES
            # ----------------------------------------------------

            tokenizer.padding_side = (
                self.padding_side
            )

            tokenizer.truncation_side = (
                self.truncation_side
            )

            # ----------------------------------------------------
            # PAD TOKEN SAFETY
            # ----------------------------------------------------

            if (
                tokenizer.pad_token
                is None
            ):

                if self.force_pad_token:

                    tokenizer.pad_token = (
                        tokenizer.eos_token
                    )

                    self.logger.warning(
                        "Pad token missing. "
                        "EOS token assigned as PAD token."
                    )

            # ----------------------------------------------------
            # FINAL VALIDATION
            # ----------------------------------------------------

            self.validate_tokenizer(
                tokenizer
            )

            self.tokenizer = tokenizer

            self.loaded = True

            self.logger.info(
                f"Tokenizer loaded successfully | "
                f"VocabSize={tokenizer.vocab_size}"
            )

            return tokenizer

        except Exception as error:

            self.logger.error(
                f"Tokenizer loading failed | "
                f"Error={error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

    # ============================================================
    # TOKENIZER VALIDATION
    # ============================================================

    def validate_tokenizer(
        self,
        tokenizer,
    ):
        """
        Validate tokenizer integrity safely.
        """

        if tokenizer is None:

            raise RuntimeError(
                "Tokenizer is None."
            )

        if tokenizer.vocab_size <= 0:

            raise RuntimeError(
                "Invalid tokenizer vocabulary."
            )

        if (
            tokenizer.eos_token
            is None
        ):

            self.logger.warning(
                "Tokenizer EOS token missing."
            )

        if (
            tokenizer.pad_token
            is None
        ):

            self.logger.warning(
                "Tokenizer PAD token missing."
            )

    # ============================================================
    # GET TOKENIZER
    # ============================================================

    def get_tokenizer(
        self,
    ):
        """
        Retrieve tokenizer safely.
        """

        if self.tokenizer is None:

            raise RuntimeError(
                "Tokenizer not loaded."
            )

        return self.tokenizer

    # ============================================================
    # TOKENIZER METADATA
    # ============================================================

    def tokenizer_metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional tokenizer metadata.
        """

        if self.tokenizer is None:

            return {

                "loaded": False,
            }

        tokenizer_type = type(
            self.tokenizer
        ).__name__

        return {

            "model_name":
                self.model_name,

            "loaded":
                self.loaded,

            "tokenizer_type":
                tokenizer_type,

            "vocab_size":
                self.tokenizer.vocab_size,

            "padding_side":
                self.tokenizer.padding_side,

            "truncation_side":
                self.tokenizer.truncation_side,

            "pad_token":
                self.tokenizer.pad_token,

            "eos_token":
                self.tokenizer.eos_token,

            "bos_token":
                self.tokenizer.bos_token,

            "unk_token":
                self.tokenizer.unk_token,

            "is_fast":
                isinstance(
                    self.tokenizer,
                    PreTrainedTokenizerFast,
                ),

            "created_at":
                self.created_at,
        }

    # ============================================================
    # TEST TOKENIZATION
    # ============================================================

    def test_tokenization(
        self,
        sample_text: str = (
            "Institutional AI systems "
            "require scalable tokenization."
        ),
    ) -> Dict[str, Any]:
        """
        Validate tokenizer execution safely.
        """

        if self.tokenizer is None:

            raise RuntimeError(
                "Tokenizer not loaded."
            )

        encoded = self.tokenizer(

            sample_text,

            return_tensors="pt",
        )

        return {

            "input_length":
                int(
                    encoded[
                        "input_ids"
                    ].shape[-1]
                ),

            "attention_mask_shape":
                tuple(
                    encoded[
                        "attention_mask"
                    ].shape
                ),

            "token_count":
                int(
                    encoded[
                        "input_ids"
                    ].numel()
                ),
        }

    # ============================================================
    # EXPORT METADATA
    # ============================================================

    def export_metadata(
        self,
        output_path: str,
    ):
        """
        Export tokenizer metadata safely.
        """

        metadata = {

            "tokenizer_metadata":
                self.tokenizer_metadata(),
        }

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(

                metadata,

                file,

                indent=4,

                ensure_ascii=False,
            )

        self.logger.info(
            f"Tokenizer metadata exported | "
            f"Path={output_path}"
        )

    # ============================================================
    # SAFE LOADER
    # ============================================================

    def safe_load_tokenizer(
        self,
    ) -> Optional[
        PreTrainedTokenizer
        | PreTrainedTokenizerFast
    ]:
        """
        Fault-tolerant tokenizer loader.
        """

        try:

            return self.load_tokenizer()

        except Exception as error:

            self.logger.error(
                f"Safe tokenizer loading failed | "
                f"Error={error}"
            )

            return None

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime summary safely.
        """

        return {

            "model_name":
                self.model_name,

            "loaded":
                self.loaded,

            "use_fast":
                self.use_fast,

            "padding_side":
                self.padding_side,

            "truncation_side":
                self.truncation_side,

            "force_pad_token":
                self.force_pad_token,
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"TokenizerLoader("
            f"model_name={self.model_name}, "
            f"loaded={self.loaded})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    loader = TokenizerLoader(

        model_name="gpt2",

        use_fast=True,
    )

    tokenizer = (
        loader.load_tokenizer()
    )

    print("\nTokenizer Summary:\n")

    print(
        json.dumps(
            loader.summary(),
            indent=4,
        )
    )

    print("\nTokenizer Metadata:\n")

    print(
        json.dumps(
            loader.tokenizer_metadata(),
            indent=4,
        )
    )

    print("\nTokenization Test:\n")

    print(
        json.dumps(
            loader.test_tokenization(),
            indent=4,
        )
    )
