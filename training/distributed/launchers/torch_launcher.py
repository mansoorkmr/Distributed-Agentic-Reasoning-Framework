"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Distributed Torch Launcher Infrastructure

Author:
    DARF Distributed Systems Division

Purpose:
    Centralized distributed execution launcher for:

        - Distributed Data Parallel (DDP)
        - Multi-GPU orchestration
        - Multi-node HPC execution
        - Elastic distributed training
        - SLURM integration
        - torchrun execution
        - fault-tolerant distributed startup

Core Responsibilities:
    - distributed environment initialization
    - torch.distributed launch orchestration
    - rank/world-size management
    - CUDA device assignment
    - backend initialization
    - distributed runtime validation
    - HPC-compatible startup
    - distributed fault handling

Design Principles:
    - deterministic
    - fault-tolerant
    - distributed-safe
    - HPC-compatible
    - production-grade
    - future extensible
    - institutionally reproducible

Supported Execution Modes:
    - single GPU
    - single-node multi-GPU
    - multi-node distributed execution
    - SLURM/HPC execution
    - elastic distributed execution
"""

import os
import sys
import socket
import traceback

import torch
import torch.distributed as dist

from infrastructure.logging.structured_logger import (
    get_logger
)

from training.distributed.utils.device_manager import (
    DeviceManager
)

from training.distributed.utils.distributed_validator import (
    DistributedValidator
)

from training.distributed.ddp.communication.process_group import (
    ProcessGroupManager
)


class TorchLauncher:
    """
    Institutional-grade distributed launch engine.

    Handles:
        - torchrun startup
        - distributed runtime initialization
        - multi-GPU orchestration
        - distributed-safe execution
        - environment validation
        - HPC-compatible launch lifecycle
    """

    SUPPORTED_BACKENDS = {

        "nccl",

        "gloo",

        "mpi",
    }

    def __init__(
        self,
        backend="nccl",
        enable_runtime_validation=True,
        enable_barrier_validation=True,
    ):

        self.backend = backend.lower()

        self.enable_runtime_validation = (
            enable_runtime_validation
        )

        self.enable_barrier_validation = (
            enable_barrier_validation
        )

        self.logger = get_logger(
            name="TorchLauncher",
            log_dir="logs/hpc",
        )

        self.device_manager = DeviceManager()

        self.validator = DistributedValidator(
            backend=self.backend
        )

        self.process_group_manager = (
            ProcessGroupManager(
                backend=self.backend,
                enable_barrier_validation=(
                    self.enable_barrier_validation
                ),
            )
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
    # MAIN LAUNCH ENTRYPOINT
    # ============================================================

    def launch(self):
        """
        Execute full distributed launch pipeline.
        """

        try:

            self.logger.info(
                "Initializing distributed launch pipeline."
            )

            self._validate_backend()

            self._log_environment()

            # ----------------------------------------------------
            # VALIDATION
            # ----------------------------------------------------

            if self.enable_runtime_validation:

                self.validator.validate_environment()

            # ----------------------------------------------------
            # PROCESS GROUP INITIALIZATION
            # ----------------------------------------------------

            self.process_group_manager.initialize()

            # ----------------------------------------------------
            # DEVICE INITIALIZATION
            # ----------------------------------------------------

            device = (
                self.device_manager.initialize_device()
            )

            self.logger.info(
                f"Distributed device initialized: "
                f"{device}"
            )

            # ----------------------------------------------------
            # CUDA SYNCHRONIZATION
            # ----------------------------------------------------

            self.device_manager.synchronize()

            # ----------------------------------------------------
            # FINAL STATUS
            # ----------------------------------------------------

            self.logger.info(
                f"Distributed launch completed successfully | "
                f"Rank={self.rank} | "
                f"WorldSize={self.world_size}"
            )

            return {

                "success": True,

                "rank": self.rank,

                "local_rank": self.local_rank,

                "world_size": self.world_size,

                "device": str(device),

                "backend": self.backend,
            }

        except Exception as error:

            self.logger.error(
                f"Distributed launch failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            self.safe_shutdown()

            raise error

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
    # ENVIRONMENT LOGGING
    # ============================================================

    def _log_environment(self):

        hostname = socket.gethostname()

        self.logger.info(
            f"Distributed Runtime Environment | "
            f"Hostname={hostname} | "
            f"Rank={self.rank} | "
            f"LocalRank={self.local_rank} | "
            f"WorldSize={self.world_size} | "
            f"MASTER_ADDR={self.master_addr} | "
            f"MASTER_PORT={self.master_port}"
        )

    # ============================================================
    # SAFE SHUTDOWN
    # ============================================================

    def safe_shutdown(self):
        """
        Fault-tolerant distributed shutdown.
        """

        try:

            self.logger.warning(
                "Executing distributed shutdown."
            )

            if dist.is_initialized():

                try:

                    dist.barrier()

                except Exception:

                    pass

            self.process_group_manager.destroy()

            self.device_manager.cleanup_memory()

            self.logger.info(
                "Distributed shutdown completed."
            )

        except Exception as error:

            self.logger.error(
                f"Distributed shutdown failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

    # ============================================================
    # DISTRIBUTED STATUS
    # ============================================================

    def export_runtime_summary(self):

        return {

            "backend": self.backend,

            "rank": self.rank,

            "local_rank": self.local_rank,

            "world_size": self.world_size,

            "master_addr": self.master_addr,

            "master_port": self.master_port,

            "cuda_available":
                torch.cuda.is_available(),

            "distributed_available":
                dist.is_available(),

            "distributed_initialized":
                dist.is_initialized(),

            "hostname":
                socket.gethostname(),
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"TorchLauncher("
            f"backend={self.backend}, "
            f"rank={self.rank}, "
            f"world_size={self.world_size})"
        )


# ================================================================
# STANDALONE EXECUTION
# ================================================================

def main():
    """
    Standalone distributed launcher entrypoint.
    """

    backend = os.environ.get(
        "DIST_BACKEND",
        "nccl",
    )

    launcher = TorchLauncher(
        backend=backend
    )

    runtime = launcher.launch()

    print("\nDistributed Runtime Initialized:\n")

    for key, value in runtime.items():

        print(f"{key}: {value}")


# ================================================================
# PYTHON ENTRYPOINT
# ================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nDistributed execution interrupted.\n"
        )

        sys.exit(1)

    except Exception as error:

        print(
            f"\nFatal distributed launcher failure: "
            f"{error}\n"
        )

        sys.exit(1)
