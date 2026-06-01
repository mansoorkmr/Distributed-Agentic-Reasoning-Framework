"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Distributed Device Management Infrastructure

Author:
    DARF Distributed Systems Division

Purpose:
    Centralized GPU/CPU device orchestration and hardware
    resource management for:

        - distributed training
        - multi-GPU execution
        - HPC orchestration
        - mixed precision execution
        - distributed inference
        - resource-aware scheduling

Core Responsibilities:
    - device discovery
    - distributed GPU assignment
    - CUDA validation
    - memory profiling
    - TF32 / cuDNN optimization
    - distributed-safe device initialization
    - compute capability validation
    - runtime hardware introspection

Design Principles:
    - deterministic
    - distributed-safe
    - HPC-compatible
    - production-grade
    - fault-tolerant
    - scalable
    - future extensible

Supported Execution Modes:
    - CPU
    - Single GPU
    - Multi-GPU DDP
    - Multi-node distributed execution
"""

import os
import platform

import torch

from infrastructure.logging.structured_logger import (
    get_logger
)


class DeviceManager:
    """
    Institutional-grade device orchestration manager.

    Handles:
        - distributed device allocation
        - CUDA initialization
        - runtime optimization
        - hardware validation
        - GPU profiling
        - distributed-safe GPU assignment
    """

    def __init__(
        self,
        enable_tf32=True,
        enable_cudnn_benchmark=True,
        deterministic=False
    ):

        self.logger = get_logger(
            name="DeviceManager",
            log_dir="logs/system"
        )

        self.enable_tf32 = enable_tf32

        self.enable_cudnn_benchmark = (
            enable_cudnn_benchmark
        )

        self.deterministic = deterministic

        self.device = None

        self.local_rank = 0

        self.world_size = 1

        self.rank = 0

        self._configure_runtime()

    # ============================================================
    # RUNTIME CONFIGURATION
    # ============================================================

    def _configure_runtime(self):
        """
        Configure low-level CUDA runtime behavior.
        """

        # --------------------------------------------------------
        # cuDNN Optimization
        # --------------------------------------------------------

        torch.backends.cudnn.benchmark = (
            self.enable_cudnn_benchmark
        )

        # --------------------------------------------------------
        # Deterministic Mode
        # --------------------------------------------------------

        torch.backends.cudnn.deterministic = (
            self.deterministic
        )

        # --------------------------------------------------------
        # TF32 Acceleration
        # --------------------------------------------------------

        if torch.cuda.is_available():

            torch.backends.cuda.matmul.allow_tf32 = (
                self.enable_tf32
            )

            torch.backends.cudnn.allow_tf32 = (
                self.enable_tf32
            )

    # ============================================================
    # DISTRIBUTED ENVIRONMENT INITIALIZATION
    # ============================================================

    def initialize_distributed_environment(self):
        """
        Initialize distributed environment variables.
        """

        self.local_rank = int(
            os.environ.get("LOCAL_RANK", 0)
        )

        self.rank = int(
            os.environ.get("RANK", 0)
        )

        self.world_size = int(
            os.environ.get("WORLD_SIZE", 1)
        )

        self.logger.info(
            f"Distributed Environment Initialized | "
            f"Rank={self.rank} | "
            f"LocalRank={self.local_rank} | "
            f"WorldSize={self.world_size}"
        )

    # ============================================================
    # DEVICE INITIALIZATION
    # ============================================================

    def initialize_device(self):
        """
        Initialize execution device safely.
        """

        self.initialize_distributed_environment()

        # --------------------------------------------------------
        # CUDA PATH
        # --------------------------------------------------------

        if torch.cuda.is_available():

            gpu_count = torch.cuda.device_count()

            if self.local_rank >= gpu_count:

                raise RuntimeError(
                    f"Invalid LOCAL_RANK={self.local_rank}. "
                    f"Available GPUs={gpu_count}"
                )

            torch.cuda.set_device(
                self.local_rank
            )

            self.device = torch.device(
                f"cuda:{self.local_rank}"
            )

            self.logger.info(
                f"CUDA device initialized: "
                f"{self.device}"
            )

            self.logger.info(
                f"GPU Name: "
                f"{torch.cuda.get_device_name(self.local_rank)}"
            )

        # --------------------------------------------------------
        # CPU FALLBACK
        # --------------------------------------------------------

        else:

            self.device = torch.device("cpu")

            self.logger.warning(
                "CUDA unavailable. "
                "Using CPU execution."
            )

        return self.device

    # ============================================================
    # DEVICE RETRIEVAL
    # ============================================================

    def get_device(self):
        """
        Retrieve initialized device.
        """

        if self.device is None:

            return self.initialize_device()

        return self.device

    # ============================================================
    # HARDWARE PROFILING
    # ============================================================

    def get_gpu_info(self):
        """
        Retrieve complete GPU profile.
        """

        if not torch.cuda.is_available():

            return {

                "cuda_available": False,

                "device_type": "cpu"
            }

        gpu_info = []

        for gpu_id in range(
            torch.cuda.device_count()
        ):

            properties = (
                torch.cuda.get_device_properties(
                    gpu_id
                )
            )

            gpu_info.append({

                "gpu_id": gpu_id,

                "name": properties.name,

                "total_memory_gb":
                    round(
                        properties.total_memory
                        / (1024 ** 3),
                        2
                    ),

                "multi_processor_count":
                    properties.multi_processor_count,

                "compute_capability":
                    (
                        f"{properties.major}."
                        f"{properties.minor}"
                    ),

                "max_threads_per_block":
                    properties.max_threads_per_block
            })

        return {

            "cuda_available": True,

            "cuda_version":
                torch.version.cuda,

            "gpu_count":
                torch.cuda.device_count(),

            "gpus":
                gpu_info
        }

    # ============================================================
    # MEMORY PROFILING
    # ============================================================

    def get_memory_status(self):
        """
        Retrieve GPU memory statistics.
        """

        if not torch.cuda.is_available():

            return None

        device_id = self.local_rank

        allocated = (
            torch.cuda.memory_allocated(device_id)
            / (1024 ** 3)
        )

        reserved = (
            torch.cuda.memory_reserved(device_id)
            / (1024 ** 3)
        )

        max_allocated = (
            torch.cuda.max_memory_allocated(device_id)
            / (1024 ** 3)
        )

        return {

            "allocated_gb":
                round(allocated, 3),

            "reserved_gb":
                round(reserved, 3),

            "max_allocated_gb":
                round(max_allocated, 3)
        }

    # ============================================================
    # MEMORY CLEANUP
    # ============================================================

    def cleanup_memory(self):
        """
        Release cached GPU memory safely.
        """

        if torch.cuda.is_available():

            torch.cuda.empty_cache()

            self.logger.info(
                "CUDA cache cleared."
            )

    # ============================================================
    # SYNCHRONIZATION
    # ============================================================

    def synchronize(self):
        """
        Synchronize CUDA execution safely.
        """

        if torch.cuda.is_available():

            torch.cuda.synchronize()

    # ============================================================
    # VALIDATION
    # ============================================================

    def validate_environment(self):
        """
        Validate distributed execution environment.
        """

        self.logger.info(
            "Validating hardware environment."
        )

        if torch.cuda.is_available():

            gpu_count = (
                torch.cuda.device_count()
            )

            if gpu_count < 1:

                raise RuntimeError(
                    "No CUDA devices detected."
                )

            self.logger.info(
                f"Detected {gpu_count} GPU(s)."
            )

        else:

            self.logger.warning(
                "CUDA unavailable."
            )

        self.logger.info(
            "Hardware environment validation completed."
        )

    # ============================================================
    # EXECUTION SUMMARY
    # ============================================================

    def export_runtime_summary(self):
        """
        Export runtime execution metadata.
        """

        return {

            "platform":
                platform.platform(),

            "python_version":
                platform.python_version(),

            "device":
                str(self.device),

            "rank":
                self.rank,

            "local_rank":
                self.local_rank,

            "world_size":
                self.world_size,

            "gpu_info":
                self.get_gpu_info(),

            "memory_status":
                self.get_memory_status()
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"DeviceManager("
            f"device={self.device}, "
            f"rank={self.rank}, "
            f"world_size={self.world_size})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    manager = DeviceManager()

    manager.validate_environment()

    device = manager.initialize_device()

    print("\nDevice Initialized:\n")

    print(device)

    print("\nGPU Information:\n")

    print(manager.get_gpu_info())

    print("\nMemory Status:\n")

    print(manager.get_memory_status())

    print("\nRuntime Summary:\n")

    print(manager.export_runtime_summary())

    manager.cleanup_memory()
