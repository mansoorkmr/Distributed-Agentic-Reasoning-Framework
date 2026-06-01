"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Distributed Process Group Infrastructure

Author:
    DARF Distributed Systems Division

Purpose:
    Centralized distributed communication orchestration layer
    for:

        - Distributed Data Parallel (DDP)
        - Multi-GPU synchronization
        - Multi-node execution
        - NCCL/GLOO backend management
        - HPC orchestration
        - Elastic distributed execution
        - Fault-tolerant synchronization

Core Responsibilities:
    - process-group initialization
    - backend lifecycle management
    - distributed synchronization
    - rank/world-size management
    - collective communication safety
    - distributed barrier coordination
    - fault-tolerant teardown
    - environment validation

Design Principles:
    - deterministic
    - distributed-safe
    - fault-tolerant
    - HPC-compatible
    - production-grade
    - future extensible
    - institutionally reproducible

Supported Backends:
    - NCCL (GPU optimized)
    - GLOO
    - MPI

Supported Modes:
    - single-node multi-GPU
    - multi-node distributed execution
    - elastic distributed training
"""

import os
import time
import traceback

import torch
import torch.distributed as dist

from infrastructure.logging.structured_logger import (
    get_logger
)


class ProcessGroupManager:
    """
    Institutional-grade distributed process-group manager.

    Handles:
        - distributed initialization
        - backend orchestration
        - synchronization
        - distributed communication lifecycle
        - fault-tolerant teardown
    """

    SUPPORTED_BACKENDS = {

        "nccl",

        "gloo",

        "mpi",
    }

    def __init__(
        self,
        backend="nccl",
        init_method="env://",
        timeout_seconds=1800,
        enable_barrier_validation=True,
    ):

        self.backend = backend.lower()

        self.init_method = init_method

        self.timeout_seconds = timeout_seconds

        self.enable_barrier_validation = (
            enable_barrier_validation
        )

        self.logger = get_logger(
            name="ProcessGroupManager",
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

        self.initialized = False

    # ============================================================
    # MAIN INITIALIZATION
    # ============================================================

    def initialize(self):
        """
        Initialize distributed process group safely.
        """

        if self.initialized:

            self.logger.warning(
                "Process group already initialized."
            )

            return

        self._validate_backend()

        self._validate_environment()

        self._initialize_backend()

        self._validate_runtime()

        self.initialized = True

        self.logger.info(
            f"Distributed process group initialized successfully | "
            f"Backend={self.backend} | "
            f"Rank={self.rank} | "
            f"WorldSize={self.world_size}"
        )

    # ============================================================
    # BACKEND VALIDATION
    # ============================================================

    def _validate_backend(self):

        if self.backend not in self.SUPPORTED_BACKENDS:

            raise ValueError(
                f"Unsupported backend: {self.backend}"
            )

        if (
            self.backend == "nccl"
            and not torch.cuda.is_available()
        ):

            raise RuntimeError(
                "NCCL backend requires CUDA."
            )

        self.logger.info(
            f"Backend validated: {self.backend}"
        )

    # ============================================================
    # ENVIRONMENT VALIDATION
    # ============================================================

    def _validate_environment(self):

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
            f"Environment Configuration | "
            f"MASTER_ADDR={self.master_addr} | "
            f"MASTER_PORT={self.master_port}"
        )

    # ============================================================
    # BACKEND INITIALIZATION
    # ============================================================

    def _initialize_backend(self):

        if dist.is_initialized():

            self.logger.warning(
                "torch.distributed already initialized."
            )

            return

        timeout = torch.distributed.timedelta(
            seconds=self.timeout_seconds
        )

        dist.init_process_group(

            backend=self.backend,

            init_method=self.init_method,

            rank=self.rank,

            world_size=self.world_size,

            timeout=timeout,
        )

        self.logger.info(
            "torch.distributed process group created."
        )

    # ============================================================
    # RUNTIME VALIDATION
    # ============================================================

    def _validate_runtime(self):

        if not dist.is_initialized():

            raise RuntimeError(
                "Distributed runtime failed to initialize."
            )

        runtime_rank = dist.get_rank()

        runtime_world_size = dist.get_world_size()

        if runtime_rank != self.rank:

            raise RuntimeError(
                f"Rank mismatch | "
                f"Environment={self.rank} | "
                f"Runtime={runtime_rank}"
            )

        if runtime_world_size != self.world_size:

            raise RuntimeError(
                f"World size mismatch | "
                f"Environment={self.world_size} | "
                f"Runtime={runtime_world_size}"
            )

        # --------------------------------------------------------
        # Barrier Synchronization Validation
        # --------------------------------------------------------

        if self.enable_barrier_validation:

            self.barrier()

        self.logger.info(
            "Distributed runtime validated successfully."
        )

    # ============================================================
    # BARRIER SYNCHRONIZATION
    # ============================================================

    def barrier(self):

        if not dist.is_initialized():

            raise RuntimeError(
                "Process group not initialized."
            )

        start_time = time.time()

        dist.barrier()

        duration = time.time() - start_time

        self.logger.info(
            f"Distributed barrier synchronization completed | "
            f"Duration={duration:.4f}s"
        )

    # ============================================================
    # COLLECTIVE COMMUNICATION
    # ============================================================

    def broadcast_tensor(
        self,
        tensor,
        src=0
    ):

        dist.broadcast(
            tensor=tensor,
            src=src
        )

        return tensor

    def all_reduce_sum(
        self,
        tensor
    ):

        dist.all_reduce(
            tensor,
            op=dist.ReduceOp.SUM
        )

        return tensor

    def all_reduce_mean(
        self,
        tensor
    ):

        dist.all_reduce(
            tensor,
            op=dist.ReduceOp.SUM
        )

        tensor /= self.world_size

        return tensor

    def gather_tensor(
        self,
        tensor,
        dst=0
    ):

        gathered = None

        if self.rank == dst:

            gathered = [

                torch.zeros_like(tensor)

                for _ in range(self.world_size)
            ]

        dist.gather(
            tensor=tensor,
            gather_list=gathered,
            dst=dst
        )

        return gathered

    # ============================================================
    # DISTRIBUTED HELPERS
    # ============================================================

    def is_main_process(self):

        return self.rank == 0

    def get_rank(self):

        return self.rank

    def get_local_rank(self):

        return self.local_rank

    def get_world_size(self):

        return self.world_size

    # ============================================================
    # SYNCHRONIZED LOGGING
    # ============================================================

    def rank_zero_log(
        self,
        message
    ):

        if self.is_main_process():

            self.logger.info(message)

    # ============================================================
    # CLEAN SHUTDOWN
    # ============================================================

    def destroy(self):
        """
        Safely destroy distributed process group.
        """

        try:

            if dist.is_initialized():

                self.barrier()

                dist.destroy_process_group()

                self.logger.info(
                    "Distributed process group destroyed successfully."
                )

        except Exception as error:

            self.logger.error(
                f"Process group destruction failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

        finally:

            self.initialized = False

    # ============================================================
    # EXECUTION SUMMARY
    # ============================================================

    def export_runtime_summary(self):

        return {

            "backend": self.backend,

            "rank": self.rank,

            "local_rank": self.local_rank,

            "world_size": self.world_size,

            "master_addr": self.master_addr,

            "master_port": self.master_port,

            "initialized": self.initialized,

            "distributed_available":
                dist.is_available(),

            "distributed_initialized":
                dist.is_initialized(),
        }

    # ============================================================
    # SAFE INITIALIZATION WRAPPER
    # ============================================================

    def safe_initialize(self):
        """
        Fault-tolerant initialization wrapper.
        """

        try:

            self.initialize()

            return True

        except Exception as error:

            self.logger.error(
                f"Process group initialization failed: "
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
            f"ProcessGroupManager("
            f"backend={self.backend}, "
            f"rank={self.rank}, "
            f"world_size={self.world_size})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    manager = ProcessGroupManager(
        backend="gloo"
    )

    print("\nRuntime Summary:\n")

    print(
        manager.export_runtime_summary()
    )
