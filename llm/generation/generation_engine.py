"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Generation Engine Infrastructure

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade transformer generation orchestration
    infrastructure for:

        - institutional LLM systems
        - distributed inference runtimes
        - agentic reasoning systems
        - scalable transformer generation
        - HPC-aware inference execution
        - multi-agent orchestration
        - production-grade decoding
        - low-latency generation pipelines

Core Responsibilities:
    - autoregressive generation
    - decoding orchestration
    - distributed-safe inference
    - KV cache integration
    - mixed precision generation
    - inference telemetry
    - runtime observability
    - institutional reproducibility

Design Principles:
    - deterministic
    - fault-tolerant
    - distributed-safe
    - production-grade
    - institutionally reproducible
    - memory optimized
    - scalable
    - future extensible

Supported Features:
    - temperature sampling
    - top-p sampling
    - top-k sampling
    - beam search support
    - KV cache acceleration
    - streaming-ready architecture
    - mixed precision inference
    - distributed-safe generation
"""

import json
import time
import traceback
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import torch
from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
)

from infrastructure.logging.structured_logger import (
    get_logger,
)

from llm.attention.kv_cache import (
    KVCacheManager,
)

from llm.runtime.execution_context import (
    ExecutionContext,
)


class GenerationEngine:
    """
    Institutional-grade transformer generation engine.

    Handles:
        - autoregressive generation
        - decoding orchestration
        - distributed-safe inference
        - KV cache acceleration
        - institutional telemetry
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        kv_cache_manager: Optional[
            KVCacheManager
        ] = None,
        enable_mixed_precision: bool = True,
        enable_telemetry: bool = True,
    ):

        self.model = model

        self.tokenizer = tokenizer

        self.kv_cache_manager = (
            kv_cache_manager
            or KVCacheManager()
        )

        self.enable_mixed_precision = (
            enable_mixed_precision
        )

        self.enable_telemetry = (
            enable_telemetry
        )

        self.logger = get_logger(
            name="GenerationEngine",
            log_dir="logs/llm",
        )

        # ========================================================
        # TELEMETRY
        # ========================================================

        self.total_generations = 0

        self.total_generated_tokens = 0

        self.failed_generations = 0

        self.created_at = (
            datetime.utcnow().isoformat()
        )

        self.logger.info(
            "GenerationEngine initialized successfully."
        )

    # ============================================================
    # VALIDATE PROMPT
    # ============================================================

    def validate_prompt(
        self,
        prompt: str,
    ):
        """
        Validate generation prompt safely.
        """

        if prompt is None:

            raise ValueError(
                "Prompt cannot be None."
            )

        if not isinstance(prompt, str):

            raise TypeError(
                "Prompt must be string."
            )

        if len(prompt.strip()) == 0:

            raise ValueError(
                "Prompt cannot be empty."
            )

    # ============================================================
    # TOKENIZE INPUT
    # ============================================================

    def tokenize_prompt(
        self,
        prompt: str,
    ) -> Dict[str, torch.Tensor]:
        """
        Tokenize prompt safely.
        """

        encoded = self.tokenizer(

            prompt,

            return_tensors="pt",

            padding=True,

            truncation=True,
        )

        encoded = {

            key: value.to(
                self.model.device
            )

            for key, value in encoded.items()
        }

        return encoded

    # ============================================================
    # MAIN GENERATION
    # ============================================================

    @torch.inference_mode()
    def generate(
        self,
        prompt: str,
        context: Optional[
            ExecutionContext
        ] = None,
    ) -> Dict[str, Any]:
        """
        Institutional-grade autoregressive generation.
        """

        generation_start = time.time()

        try:

            self.validate_prompt(prompt)

            if context is None:

                context = ExecutionContext(
                    user_query=prompt
                )

            context.start_execution()

            inputs = self.tokenize_prompt(
                prompt
            )

            generation_kwargs = {

                "max_new_tokens":
                    context.max_new_tokens,

                "temperature":
                    context.temperature,

                "top_p":
                    context.top_p,

                "top_k":
                    context.top_k,

                "repetition_penalty":
                    context.repetition_penalty,

                "do_sample":
                    context.do_sample,

                "use_cache":
                    context.use_cache,

                "pad_token_id":
                    self.tokenizer.pad_token_id,

                "eos_token_id":
                    self.tokenizer.eos_token_id,

                "return_dict_in_generate":
                    True,

                "output_scores":
                    False,
            }

            # ----------------------------------------------------
            # MIXED PRECISION
            # ----------------------------------------------------

            if (
                self.enable_mixed_precision
                and torch.cuda.is_available()
            ):

                with torch.autocast(

                    device_type="cuda",

                    dtype=torch.bfloat16,
                ):

                    outputs = (
                        self.model.generate(

                            **inputs,

                            **generation_kwargs,
                        )
                    )

            else:

                outputs = self.model.generate(

                    **inputs,

                    **generation_kwargs,
                )

            generated_sequence = (
                outputs.sequences[0]
            )

            generated_text = (
                self.tokenizer.decode(

                    generated_sequence,

                    skip_special_tokens=True,
                )
            )

            # ----------------------------------------------------
            # GENERATED TOKEN COUNT
            # ----------------------------------------------------

            generated_tokens = int(

                generated_sequence.shape[-1]
            )

            self.total_generations += 1

            self.total_generated_tokens += (
                generated_tokens
            )

            generation_end = time.time()

            latency = (
                generation_end
                - generation_start
            )

            context.complete_execution(

                success=True,

                tokens_generated=(
                    generated_tokens
                ),
            )

            # ----------------------------------------------------
            # STORE KV CACHE
            # ----------------------------------------------------

            if (
                context.use_cache
                and hasattr(
                    outputs,
                    "past_key_values",
                )
            ):

                self.kv_cache_manager.store(

                    request_id=(
                        context.request_id
                    ),

                    past_key_values=(
                        outputs.past_key_values
                    ),
                )

            result = {

                "request_id":
                    context.request_id,

                "generated_text":
                    generated_text,

                "generated_tokens":
                    generated_tokens,

                "latency_seconds":
                    round(latency, 4),

                "success":
                    True,

                "execution_summary":
                    context.summary(),
            }

            self.logger.info(
                f"Generation completed | "
                f"RequestID={context.request_id} | "
                f"Tokens={generated_tokens} | "
                f"Latency={latency:.4f}s"
            )

            return result

        except Exception as error:

            self.failed_generations += 1

            generation_end = time.time()

            latency = (
                generation_end
                - generation_start
            )

            if context is not None:

                context.fail_execution(
                    str(error)
                )

            self.logger.error(
                f"Generation failed | "
                f"Error={error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            return {

                "generated_text":
                    None,

                "generated_tokens":
                    0,

                "latency_seconds":
                    round(latency, 4),

                "success":
                    False,

                "error":
                    str(error),
            }

    # ============================================================
    # BATCH GENERATION
    # ============================================================

    @torch.inference_mode()
    def generate_batch(
        self,
        prompts: List[str],
        max_new_tokens: int = 256,
    ) -> List[Dict[str, Any]]:
        """
        Distributed-safe batch generation.
        """

        if not isinstance(prompts, list):

            raise TypeError(
                "Prompts must be list."
            )

        results = []

        for prompt in prompts:

            context = ExecutionContext(

                user_query=prompt,

                max_new_tokens=(
                    max_new_tokens
                ),
            )

            result = self.generate(

                prompt=prompt,

                context=context,
            )

            results.append(result)

        return results

    # ============================================================
    # GPU MEMORY SUMMARY
    # ============================================================

    def gpu_memory_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional GPU telemetry.
        """

        if not torch.cuda.is_available():

            return {

                "cuda_available":
                    False
            }

        allocated = (
            torch.cuda.memory_allocated()
            / (1024 ** 3)
        )

        reserved = (
            torch.cuda.memory_reserved()
            / (1024 ** 3)
        )

        max_allocated = (
            torch.cuda.max_memory_allocated()
            / (1024 ** 3)
        )

        return {

            "cuda_available":
                True,

            "allocated_gb":
                round(
                    allocated,
                    4,
                ),

            "reserved_gb":
                round(
                    reserved,
                    4,
                ),

            "max_allocated_gb":
                round(
                    max_allocated,
                    4,
                ),
        }

    # ============================================================
    # TELEMETRY
    # ============================================================

    def telemetry(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional runtime telemetry.
        """

        avg_tokens = 0.0

        if self.total_generations > 0:

            avg_tokens = (

                self.total_generated_tokens

                / self.total_generations
            )

        return {

            "total_generations":
                self.total_generations,

            "total_generated_tokens":
                self.total_generated_tokens,

            "failed_generations":
                self.failed_generations,

            "average_generated_tokens":
                round(
                    avg_tokens,
                    4,
                ),

            "created_at":
                self.created_at,
        }

    # ============================================================
    # EXPORT TELEMETRY
    # ============================================================

    def export_telemetry(
        self,
        output_path: str,
    ):
        """
        Export runtime telemetry safely.
        """

        exported = {

            "telemetry":
                self.telemetry(),

            "gpu_memory":
                self.gpu_memory_summary(),
        }

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(

                exported,

                file,

                indent=4,

                ensure_ascii=False,
            )

        self.logger.info(
            f"Generation telemetry exported | "
            f"Path={output_path}"
        )

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(
        self,
    ):
        """
        Cleanup generation resources safely.
        """

        try:

            self.kv_cache_manager.clear()

            if torch.cuda.is_available():

                torch.cuda.empty_cache()

            self.logger.info(
                "GenerationEngine cleanup completed."
            )

        except Exception as error:

            self.logger.error(
                f"Cleanup failed | "
                f"Error={error}"
            )

    # ============================================================
    # SUMMARY
    # ============================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional runtime summary.
        """

        return {

            "model_device":
                str(self.model.device),

            "mixed_precision":
                self.enable_mixed_precision,

            "telemetry_enabled":
                self.enable_telemetry,

            "total_generations":
                self.total_generations,

            "created_at":
                self.created_at,
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"GenerationEngine("
            f"generations={self.total_generations}, "
            f"failed={self.failed_generations})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
    )

    model_name = "gpt2"

    tokenizer = (
        AutoTokenizer
        .from_pretrained(model_name)
    )

    model = (
        AutoModelForCausalLM
        .from_pretrained(model_name)
    )

    engine = GenerationEngine(

        model=model,

        tokenizer=tokenizer,
    )

    result = engine.generate(

        prompt=(
            "Explain distributed "
            "agentic reasoning systems."
        )
    )

    print("\nGeneration Result:\n")

    print(
        json.dumps(
            result,
            indent=4,
        )
    )

    print("\nTelemetry:\n")

    print(
        json.dumps(
            engine.telemetry(),
            indent=4,
        )
    )
