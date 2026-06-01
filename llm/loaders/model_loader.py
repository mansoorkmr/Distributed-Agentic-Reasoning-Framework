"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Model Loader Infrastructure

Author:
    DARF Runtime Systems Division

Purpose:
    Enterprise-grade transformer model loading and orchestration
    infrastructure for:

        - institutional LLM systems
        - distributed inference pipelines
        - HPC transformer execution
        - scalable AI runtime systems
        - agentic reasoning infrastructure
        - mixed precision execution
        - distributed-safe loading
        - production-grade deployment

Core Responsibilities:
    - transformer model loading
    - distributed-safe initialization
    - checkpoint orchestration
    - mixed precision runtime setup
    - memory-aware loading
    - device-aware execution
    - quantization readiness
    - institutional observability

Design Principles:
    - deterministic
    - fault-tolerant
    - distributed-safe
    - production-grade
    - institutionally reproducible
    - scalable
    - memory optimized
    - future extensible

Supported Features:
    - AutoModelForCausalLM loading
    - bf16/fp16/fp32 runtime
    - distributed-safe loading
    - device map orchestration
    - safetensors support
    - low-memory initialization
    - inference optimization
    - runtime telemetry
"""

import gc
import json
import os
import traceback
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

import torch
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
)

from infrastructure.logging.structured_logger import (
    get_logger,
)


class ModelLoader:
    """
    Institutional-grade transformer model loader.

    Handles:
        - distributed-safe model loading
        - mixed precision initialization
        - memory-aware orchestration
        - institutional inference setup
        - scalable runtime preparation
    """

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        model_name: str,
        device: str = "cuda",
        precision: str = "bf16",
        low_cpu_mem_usage: bool = True,
        trust_remote_code: bool = False,
        use_safetensors: bool = True,
        device_map: str = "auto",
        compile_model: bool = False,
        gradient_checkpointing: bool = False,
    ):

        self.model_name = model_name

        self.device = device

        self.precision = precision

        self.low_cpu_mem_usage = (
            low_cpu_mem_usage
        )

        self.trust_remote_code = (
            trust_remote_code
        )

        self.use_safetensors = (
            use_safetensors
        )

        self.device_map = device_map

        self.compile_model = compile_model

        self.gradient_checkpointing = (
            gradient_checkpointing
        )

        self.logger = get_logger(
            name="ModelLoader",
            log_dir="logs/llm",
        )

        # ========================================================
        # RUNTIME STATE
        # ========================================================

        self.model = None

        self.config = None

        self.loaded = False

        self.created_at = (
            datetime.utcnow().isoformat()
        )

        self.logger.info(
            f"ModelLoader initialized | "
            f"Model={self.model_name}"
        )

    # ============================================================
    # RESOLVE TORCH DTYPE
    # ============================================================

    def resolve_dtype(
        self,
    ) -> torch.dtype:
        """
        Resolve institutional runtime precision.
        """

        precision = (
            self.precision.lower()
        )

        if precision == "fp16":

            return torch.float16

        if precision == "bf16":

            return torch.bfloat16

        if precision == "fp32":

            return torch.float32

        raise ValueError(
            f"Unsupported precision: "
            f"{self.precision}"
        )

    # ============================================================
    # VALIDATE ENVIRONMENT
    # ============================================================

    def validate_environment(
        self,
    ):
        """
        Validate runtime environment safely.
        """

        if self.device == "cuda":

            if not torch.cuda.is_available():

                raise RuntimeError(
                    "CUDA requested but unavailable."
                )

        if self.precision == "bf16":

            if (
                self.device == "cuda"
                and not torch.cuda.is_bf16_supported()
            ):

                self.logger.warning(
                    "bf16 unsupported on current GPU. "
                    "Falling back may be required."
                )

    # ============================================================
    # LOAD MODEL CONFIG
    # ============================================================

    def load_config(
        self,
    ):
        """
        Load transformer configuration safely.
        """

        self.config = AutoConfig.from_pretrained(

            self.model_name,

            trust_remote_code=(
                self.trust_remote_code
            ),
        )

        self.logger.info(
            f"Model configuration loaded | "
            f"HiddenSize="
            f"{getattr(self.config, 'hidden_size', 'unknown')}"
        )

        return self.config

    # ============================================================
    # LOAD MODEL
    # ============================================================

    def load_model(
        self,
    ):
        """
        Load institutional transformer model safely.
        """

        try:

            self.validate_environment()

            dtype = self.resolve_dtype()

            if self.config is None:

                self.load_config()

            self.logger.info(
                f"Loading transformer model | "
                f"Model={self.model_name} | "
                f"Precision={self.precision}"
            )

            self.model = (
                AutoModelForCausalLM
                .from_pretrained(

                    self.model_name,

                    config=self.config,

                    torch_dtype=dtype,

                    low_cpu_mem_usage=(
                        self.low_cpu_mem_usage
                    ),

                    trust_remote_code=(
                        self.trust_remote_code
                    ),

                    use_safetensors=(
                        self.use_safetensors
                    ),

                    device_map=self.device_map,
                )
            )

            # ----------------------------------------------------
            # GRADIENT CHECKPOINTING
            # ----------------------------------------------------

            if self.gradient_checkpointing:

                if hasattr(

                    self.model,

                    "gradient_checkpointing_enable",
                ):

                    self.model.gradient_checkpointing_enable()

                    self.logger.info(
                        "Gradient checkpointing enabled."
                    )

            # ----------------------------------------------------
            # MODEL COMPILATION
            # ----------------------------------------------------

            if (

                self.compile_model

                and hasattr(torch, "compile")
            ):

                self.logger.info(
                    "Compiling transformer model."
                )

                self.model = torch.compile(
                    self.model
                )

            # ----------------------------------------------------
            # EVAL MODE
            # ----------------------------------------------------

            self.model.eval()

            self.loaded = True

            self.logger.info(
                f"Transformer model loaded successfully | "
                f"Model={self.model_name}"
            )

            return self.model

        except Exception as error:

            self.logger.error(
                f"Model loading failed | "
                f"Error={error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

    # ============================================================
    # GET MODEL
    # ============================================================

    def get_model(
        self,
    ):
        """
        Retrieve loaded model safely.
        """

        if self.model is None:

            raise RuntimeError(
                "Model not loaded."
            )

        return self.model

    # ============================================================
    # MODEL METADATA
    # ============================================================

    def model_metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Return institutional model metadata.
        """

        if self.model is None:

            return {

                "loaded": False,
            }

        parameter_count = sum(

            parameter.numel()

            for parameter in self.model.parameters()
        )

        trainable_parameters = sum(

            parameter.numel()

            for parameter in self.model.parameters()

            if parameter.requires_grad
        )

        return {

            "model_name":
                self.model_name,

            "precision":
                self.precision,

            "device":
                self.device,

            "loaded":
                self.loaded,

            "parameter_count":
                parameter_count,

            "trainable_parameters":
                trainable_parameters,

            "dtype":
                str(
                    next(
                        self.model.parameters()
                    ).dtype
                ),

            "created_at":
                self.created_at,
        }

    # ============================================================
    # GPU MEMORY METRICS
    # ============================================================

    def gpu_memory_summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return GPU memory telemetry.
        """

        if not torch.cuda.is_available():

            return {

                "cuda_available": False
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
    # EXPORT METADATA
    # ============================================================

    def export_metadata(
        self,
        output_path: str,
    ):
        """
        Export runtime metadata safely.
        """

        metadata = {

            "model_metadata":
                self.model_metadata(),

            "gpu_memory":
                self.gpu_memory_summary(),
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
            f"Model metadata exported | "
            f"Path={output_path}"
        )

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(
        self,
    ):
        """
        Cleanup model resources safely.
        """

        try:

            if self.model is not None:

                del self.model

                self.model = None

            gc.collect()

            if torch.cuda.is_available():

                torch.cuda.empty_cache()

            self.loaded = False

            self.logger.info(
                "Model cleanup completed successfully."
            )

        except Exception as error:

            self.logger.error(
                f"Cleanup failed | "
                f"Error={error}"
            )

    # ============================================================
    # SAFE LOADER
    # ============================================================

    def safe_load_model(
        self,
    ):
        """
        Fault-tolerant model loading wrapper.
        """

        try:

            return self.load_model()

        except Exception as error:

            self.logger.error(
                f"Safe model loading failed | "
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
        Return institutional runtime summary.
        """

        return {

            "model_name":
                self.model_name,

            "device":
                self.device,

            "precision":
                self.precision,

            "loaded":
                self.loaded,

            "device_map":
                self.device_map,

            "gradient_checkpointing":
                self.gradient_checkpointing,

            "compile_model":
                self.compile_model,
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"ModelLoader("
            f"model_name={self.model_name}, "
            f"precision={self.precision}, "
            f"loaded={self.loaded})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    loader = ModelLoader(

        model_name="gpt2",

        precision="fp32",

        device="cpu",
    )

    model = loader.load_model()

    print("\nModel Summary:\n")

    print(
        json.dumps(
            loader.summary(),
            indent=4,
        )
    )

    print("\nModel Metadata:\n")

    print(
        json.dumps(
            loader.model_metadata(),
            indent=4,
        )
    )
