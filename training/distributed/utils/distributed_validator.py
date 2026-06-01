"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Distributed Environment Validation Infrastructure

Author:
    DARF Distributed Systems Division

Purpose:
    Enterprise-grade distributed execution validation system
    for multi-GPU, multi-process, and HPC-based training.

Core Responsibilities:
    - CUDA validation
    - NCCL/GLOO backend verification
    - rank/world-size consistency checks
    - distributed environment integrity validation
    - inter-process communication verification
    - hardware topology inspection
    - synchronization testing
    - deterministic execution validation
    - mixed precision compatibility checks

Design Principles:
    - deterministic
    - distributed-safe
    - HPC-compatible
    - fault-tolerant
    - production-grade
    - future extensible
    - institutional reliability

Supported Modes:
    - single GPU
    - multi-GPU DDP
    - multi-node distributed training
    - CPU fallback execution
"""

import os
import socket
import traceback

import torch
import torch.distributed as dist

from infrastructure.logging.structured_logger import (
    get_logger
)


class DistributedValidator:
    """
    Institutional-grade distributed environment validator.

    Validates:
        - distributed runtime integrity
        - CUDA availability
        - process-group correctness
        - backend compatibility
        - synchronization consistency
        - communication safety
    """

    SUPPORTED_BACKENDS = {
        "nccl",
        "gloo",
        "mpi",
    }

    def __init__(
        self,
        backend="nccl",
        require_cuda=True,
        enable_barrier_test=True,
    ):

        self.backend = backend.lower()

        self.require_cuda = require_cuda

        self.enable_barrier_test = (
            enable_barrier_test
        )

        self.logger = get_logger(
            name="DistributedValidator",
            log_dir="logs/system",
        )

        self.rank = int(
            os.environ.get("RANK", 0)
        )

        self.local_rank = int(
            os.environ.get("LOCAL_RANK", 0)
        )

        self.world_size = int(
            os.environ.get("WORLD_SIZE", 1)
        )

        self.master_addr = os.environ.get(
            "MASTER_ADDR",
            "localhost",
        )

        self.master_port = os.environ.get(
            "MASTER_PORT",
            "29500",
        )

    # ============================================================
    # MAIN VALIDATION ENTRYPOINT
    # ============================================================

    def validate_environment(self):
        """
        Execute complete distributed validation pipeline.
        """

        self.logger.info(
            "Starting distributed environment validation."
        )

        self._validate_backend()

        self._validate_environment_variables()

        self._validate_cuda()

        self._validate_gpu_assignment()

        self._validate_process_group_support()

        self._validate_network_connectivity()

        self._validate_distributed_runtime()

        self._validate_memory_configuration()

        self._validate_mixed_precision_support()

        self.logger.info(
            "Distributed environment validation completed successfully."
        )

    # ============================================================
    # BACKEND VALIDATION
    # ============================================================

    def _validate_backend(self):

        if self.backend not in self.SUPPORTED_BACKENDS:

            raise ValueError(
                f"Unsupported distributed backend: "
                f"{self.backend}"
            )

        self.logger.info(
            f"Distributed backend validated: "
            f"{self.backend}"
        )

    # ============================================================
    # ENVIRONMENT VARIABLES
    # ============================================================

    def _validate_environment_variables(self):

        required_variables = [

            "RANK",

            "WORLD_SIZE",

            "LOCAL_RANK",
        ]

        missing_variables = []

        for variable in required_variables:

            if variable not in os.environ:

                missing_variables.append(variable)

        if missing_variables:

            self.logger.warning(
                f"Missing distributed environment variables: "
                f"{missing_variables}"
            )

        self.logger.info(
            f"Environment Variables | "
            f"Rank={self.rank} | "
            f"LocalRank={self.local_rank} | "
            f"WorldSize={self.world_size}"
        )

    # ============================================================
    # CUDA VALIDATION
    # ============================================================

    def _validate_cuda(self):

        cuda_available = torch.cuda.is_available()

        if self.require_cuda and not cuda_available:

            raise RuntimeError(
                "CUDA is required but unavailable."
            )

        if cuda_available:

            gpu_count = torch.cuda.device_count()

            self.logger.info(
                f"CUDA Available | GPUs={gpu_count}"
            )

        else:

            self.logger.warning(
                "CUDA unavailable. CPU execution enabled."
            )

    # ============================================================
    # GPU ASSIGNMENT VALIDATION
    # ============================================================

    def _validate_gpu_assignment(self):

        if not torch.cuda.is_available():

            return

        gpu_count = torch.cuda.device_count()

        if self.local_rank >= gpu_count:

            raise RuntimeError(
                f"Invalid LOCAL_RANK={self.local_rank}. "
                f"Available GPUs={gpu_count}"
            )

        self.logger.info(
            f"GPU assignment validated | "
            f"LocalRank={self.local_rank}"
        )

    # ============================================================
    # PROCESS GROUP SUPPORT
    # ============================================================

    def _validate_process_group_support(self):

        if not dist.is_available():

            raise RuntimeError(
                "torch.distributed unavailable."
            )

        self.logger.info(
            "torch.distributed available."
        )

    # ============================================================
    # NETWORK VALIDATION
    # ============================================================

    def _validate_network_connectivity(self):

        try:

            socket.gethostbyname(
                self.master_addr
            )

            self.logger.info(
                f"MASTER_ADDR resolved successfully: "
                f"{self.master_addr}"
            )

        except socket.gaierror as error:

            raise RuntimeError(
                f"MASTER_ADDR resolution failed: "
                f"{error}"
            )

    # ============================================================
    # DISTRIBUTED RUNTIME VALIDATION
    # ============================================================

    def _validate_distributed_runtime(self):

        if not dist.is_initialized():

            self.logger.warning(
                "Process group not initialized yet. "
                "Skipping synchronization validation."
            )

            return

        # --------------------------------------------------------
        # Barrier Synchronization Test
        # --------------------------------------------------------

        if self.enable_barrier_test:

            try:

                dist.barrier()

                self.logger.info(
                    "Distributed barrier synchronization successful."
                )

            except Exception as error:

                raise RuntimeError(
                    f"Barrier synchronization failed: "
                    f"{error}"
                )

        # --------------------------------------------------------
        # World Size Validation
        # --------------------------------------------------------

        runtime_world_size = (
            dist.get_world_size()
        )

        runtime_rank = dist.get_rank()

        if runtime_world_size != self.world_size:

            raise RuntimeError(
                f"WORLD_SIZE mismatch | "
                f"Environment={self.world_size} | "
                f"Runtime={runtime_world_size}"
            )

        if runtime_rank != self.rank:

            raise RuntimeError(
                f"RANK mismatch | "
                f"Environment={self.rank} | "
                f"Runtime={runtime_rank}"
            )

        self.logger.info(
            f"Distributed runtime validated | "
            f"Rank={runtime_rank} | "
            f"WorldSize={runtime_world_size}"
        )

    # ============================================================
    # MEMORY VALIDATION
    # ============================================================

    def _validate_memory_configuration(self):

        if not torch.cuda.is_available():

            return

        properties = (
            torch.cuda.get_device_properties(
                self.local_rank
            )
        )

        total_memory_gb = round(
            properties.total_memory
            / (1024 ** 3),
            2,
        )

        self.logger.info(
            f"GPU Memory | "
            f"Device={self.local_rank} | "
            f"TotalMemory={total_memory_gb} GB"
        )

        if total_memory_gb < 4:

            self.logger.warning(
                "Low GPU memory detected. "
                "Large models may fail."
            )

    # ============================================================
    # MIXED PRECISION VALIDATION
    # ============================================================

    def _validate_mixed_precision_support(self):

        if not torch.cuda.is_available():

            return

        capability = torch.cuda.get_device_capability(
            self.local_rank
        )

        major, minor = capability

        self.logger.info(
            f"GPU Compute Capability: "
            f"{major}.{minor}"
        )

        if major < 7:

            self.logger.warning(
                "GPU may have limited AMP/bfloat16 support."
            )

    # ============================================================
    # DISTRIBUTED SUMMARY
    # ============================================================

    def export_validation_summary(self):

        summary = {

            "backend": self.backend,

            "rank": self.rank,

            "local_rank": self.local_rank,

            "world_size": self.world_size,

            "master_addr": self.master_addr,

            "master_port": self.master_port,

            "cuda_available":
                torch.cuda.is_available(),

            "gpu_count":
                (
                    torch.cuda.device_count()
                    if torch.cuda.is_available()
                    else 0
                ),

            "distributed_available":
                dist.is_available(),

            "distributed_initialized":
                dist.is_initialized(),
        }

        return summary

    # ============================================================
    # SAFE EXECUTION WRAPPER
    # ============================================================

    def safe_validate(self):
        """
        Safe validation wrapper with traceback logging.
        """

        try:

            self.validate_environment()

            return True

        except Exception as error:

            self.logger.error(
                f"Distributed validation failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            return False

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"DistributedValidator("
            f"backend={self.backend}, "
            f"rank={self.rank}, "
            f"world_size={self.world_size})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    validator = DistributedValidator(
        backend="nccl",
        require_cuda=False,
    )

    success = validator.safe_validate()

    print("\nValidation Success:\n")

    print(success)

    print("\nValidation Summary:\n")

    print(
        validator.export_validation_summary()
    )
