"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade HPC Launch Orchestration Infrastructure

Author:
    DARF HPC Systems Division

Purpose:
    Enterprise-grade HPC orchestration and distributed launch
    engine for:

        - Distributed AI training
        - Multi-node GPU execution
        - SLURM orchestration
        - Elastic distributed training
        - HPC runtime lifecycle management
        - Institutional workload scheduling
        - Cluster-aware execution
        - Fault-tolerant orchestration

Core Responsibilities:
    - distributed launch orchestration
    - HPC runtime initialization
    - SLURM-aware execution
    - GPU scheduling integration
    - cluster resource validation
    - distributed-safe startup
    - runtime telemetry orchestration
    - institutional execution reproducibility

Design Principles:
    - deterministic
    - fault-tolerant
    - distributed-safe
    - HPC-compatible
    - production-grade
    - institutionally reproducible
    - future extensible

Supported Execution Modes:
    - local CPU execution
    - single GPU
    - multi-GPU DDP
    - multi-node distributed execution
    - SLURM cluster orchestration
    - elastic distributed runtime
"""

import json
import os
import signal
import sys
import time
import traceback
from datetime import datetime

import torch
import torch.distributed as dist

from infrastructure.logging.structured_logger import (
    get_logger
)

from hpc.runtime.runtime_manager import (
    RuntimeManager
)

from hpc.slurm.slurm_manager import (
    SlurmManager
)

from hpc.schedulers.gpu_scheduler import (
    GPUScheduler
)

from hpc.validators.node_validator import (
    NodeValidator
)

from hpc.profiling.resource_profiler import (
    ResourceProfiler
)

from training.distributed.ddp.communication.process_group import (
    ProcessGroupManager
)


class HPCLauncher:
    """
    Institutional-grade HPC launch orchestration engine.

    Handles:
        - distributed startup orchestration
        - SLURM-aware execution
        - runtime validation
        - cluster-safe initialization
        - GPU allocation orchestration
        - distributed lifecycle management
    """

    def __init__(
        self,
        backend="nccl",
        validate_node=True,
        enable_gpu_scheduling=True,
        enable_runtime_profiling=True,
    ):

        self.backend = backend

        self.validate_node_flag = (
            validate_node
        )

        self.enable_gpu_scheduling = (
            enable_gpu_scheduling
        )

        self.enable_runtime_profiling = (
            enable_runtime_profiling
        )

        self.logger = get_logger(
            name="HPCLauncher",
            log_dir="logs/hpc",
        )

        # ========================================================
        # DISTRIBUTED ENVIRONMENT
        # ========================================================

        self.rank = int(
            os.environ.get("RANK", 0)
        )

        self.local_rank = int(
            os.environ.get("LOCAL_RANK", 0)
        )

        self.world_size = int(
            os.environ.get("WORLD_SIZE", 1)
        )

        # ========================================================
        # HPC COMPONENTS
        # ========================================================

        self.runtime_manager = (
            RuntimeManager()
        )

        self.slurm_manager = (
            SlurmManager()
        )

        self.gpu_scheduler = (
            GPUScheduler()
        )

        self.node_validator = (
            NodeValidator()
        )

        self.resource_profiler = (
            ResourceProfiler()
        )

        self.process_group_manager = (
            ProcessGroupManager(
                backend=self.backend
            )
        )

        # ========================================================
        # EXECUTION STATE
        # ========================================================

        self.launch_timestamp = (
            datetime.utcnow().isoformat()
        )

        self.initialized = False

    # ============================================================
    # MAIN HPC LAUNCH PIPELINE
    # ============================================================

    def launch(self):
        """
        Execute complete institutional-grade HPC launch pipeline.
        """

        try:

            self.logger.info(
                "Starting HPC orchestration pipeline."
            )

            # ----------------------------------------------------
            # VALIDATE NODE
            # ----------------------------------------------------

            if self.validate_node_flag:

                self._validate_node()

            # ----------------------------------------------------
            # VALIDATE SLURM
            # ----------------------------------------------------

            self._validate_slurm_environment()

            # ----------------------------------------------------
            # INITIALIZE GPU SCHEDULER
            # ----------------------------------------------------

            if self.enable_gpu_scheduling:

                self._initialize_gpu_scheduler()

            # ----------------------------------------------------
            # INITIALIZE DISTRIBUTED RUNTIME
            # ----------------------------------------------------

            self._initialize_distributed_runtime()

            # ----------------------------------------------------
            # PROFILE RESOURCES
            # ----------------------------------------------------

            if self.enable_runtime_profiling:

                self._profile_resources()

            # ----------------------------------------------------
            # REGISTER SIGNAL HANDLERS
            # ----------------------------------------------------

            self._register_signal_handlers()

            self.initialized = True

            self.logger.info(
                f"HPC orchestration initialized successfully | "
                f"Rank={self.rank} | "
                f"WorldSize={self.world_size}"
            )

            return self.export_runtime_summary()

        except Exception as error:

            self.logger.error(
                f"HPC launch failed: {error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            self.safe_shutdown()

            raise error

    # ============================================================
    # NODE VALIDATION
    # ============================================================

    def _validate_node(self):

        self.logger.info(
            "Validating HPC node integrity."
        )

        report = (
            self.node_validator.validate_node()
        )

        self.logger.info(
            "Node validation successful."
        )

        return report

    # ============================================================
    # SLURM VALIDATION
    # ============================================================

    def _validate_slurm_environment(self):

        slurm_detected = (
            self.slurm_manager.detect_slurm_environment()
        )

        if slurm_detected:

            self.logger.info(
                "SLURM environment detected."
            )

            self.slurm_manager.validate_slurm_environment()

        else:

            self.logger.warning(
                "Execution outside SLURM environment."
            )

    # ============================================================
    # GPU SCHEDULER INITIALIZATION
    # ============================================================

    def _initialize_gpu_scheduler(self):

        if not torch.cuda.is_available():

            self.logger.warning(
                "CUDA unavailable. "
                "GPU scheduling skipped."
            )

            return

        selected_gpu = (
            self.gpu_scheduler.assign_gpu()
        )

        self.logger.info(
            f"GPU assigned successfully | "
            f"GPU={selected_gpu}"
        )

    # ============================================================
    # DISTRIBUTED INITIALIZATION
    # ============================================================

    def _initialize_distributed_runtime(self):

        distributed_enabled = (
            self.world_size > 1
        )

        if not distributed_enabled:

            self.logger.info(
                "Single-process execution detected."
            )

            return

        self.logger.info(
            "Initializing distributed process group."
        )

        self.process_group_manager.initialize()

        self.logger.info(
            "Distributed runtime initialized successfully."
        )

    # ============================================================
    # RESOURCE PROFILING
    # ============================================================

    def _profile_resources(self):

        profile = (
            self.resource_profiler.profile_system()
        )

        self.logger.info(
            f"Resource profiling completed | "
            f"Rank={self.rank}"
        )

        return profile

    # ============================================================
    # SIGNAL HANDLERS
    # ============================================================

    def _register_signal_handlers(self):

        signal.signal(
            signal.SIGINT,
            self._signal_handler
        )

        signal.signal(
            signal.SIGTERM,
            self._signal_handler
        )

        self.logger.info(
            "Signal handlers registered."
        )

    # ============================================================
    # SIGNAL CALLBACK
    # ============================================================

    def _signal_handler(
        self,
        signum,
        frame,
    ):
        """
        Handle HPC termination signals safely.
        """

        self.logger.warning(
            f"Received termination signal: "
            f"{signum}"
        )

        self.safe_shutdown()

        sys.exit(0)

    # ============================================================
    # DISTRIBUTED BARRIER
    # ============================================================

    def synchronize(self):
        """
        Global distributed synchronization barrier.
        """

        if dist.is_initialized():

            dist.barrier()

    # ============================================================
    # SAFE SHUTDOWN
    # ============================================================

    def safe_shutdown(self):
        """
        Institutional-grade fault-tolerant shutdown.
        """

        try:

            self.logger.warning(
                "Executing HPC shutdown pipeline."
            )

            if dist.is_initialized():

                try:

                    dist.barrier()

                except Exception:

                    pass

            # ----------------------------------------------------
            # DESTROY PROCESS GROUP
            # ----------------------------------------------------

            self.process_group_manager.destroy()

            # ----------------------------------------------------
            # CLEANUP GPU MEMORY
            # ----------------------------------------------------

            if torch.cuda.is_available():

                torch.cuda.empty_cache()

                torch.cuda.ipc_collect()

            self.logger.info(
                "HPC shutdown completed successfully."
            )

        except Exception as error:

            self.logger.error(
                f"HPC shutdown failure: {error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

    # ============================================================
    # EXECUTION STATUS
    # ============================================================

    def is_distributed(self):

        return self.world_size > 1

    def is_main_process(self):

        return self.rank == 0

    # ============================================================
    # RUNTIME SUMMARY
    # ============================================================

    def export_runtime_summary(self):

        return {

            "launch_timestamp":
                self.launch_timestamp,

            "initialized":
                self.initialized,

            "backend":
                self.backend,

            "distributed_enabled":
                self.is_distributed(),

            "rank":
                self.rank,

            "local_rank":
                self.local_rank,

            "world_size":
                self.world_size,

            "cuda_available":
                torch.cuda.is_available(),

            "gpu_count":
                (
                    torch.cuda.device_count()
                    if torch.cuda.is_available()
                    else 0
                ),

            "slurm_enabled":
                self.slurm_manager.detect_slurm_environment(),
        }

    # ============================================================
    # EXPORT EXECUTION REPORT
    # ============================================================

    def export_execution_report(
        self,
        output_path=None,
    ):
        """
        Export complete HPC runtime report.
        """

        report = {

            "runtime":
                self.runtime_manager.collect_runtime_metadata(),

            "slurm":
                self.slurm_manager.collect_slurm_metadata(),

            "resources":
                self.resource_profiler.profile_system(),

            "launcher":
                self.export_runtime_summary(),
        }

        if output_path is not None:

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
                    report,
                    file,
                    indent=4,
                )

            self.logger.info(
                f"Execution report exported: "
                f"{output_path}"
            )

        return report

    # ============================================================
    # WAIT LOOP
    # ============================================================

    def wait_forever(
        self,
        sleep_seconds=30,
    ):
        """
        Persistent runtime loop for daemonized execution.
        """

        self.logger.info(
            "Entering persistent HPC runtime loop."
        )

        try:

            while True:

                time.sleep(sleep_seconds)

        except KeyboardInterrupt:

            self.logger.warning(
                "Persistent runtime interrupted."
            )

            self.safe_shutdown()

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"HPCLauncher("
            f"backend={self.backend}, "
            f"rank={self.rank}, "
            f"world_size={self.world_size})"
        )


# ================================================================
# STANDALONE EXECUTION
# ================================================================

def main():

    launcher = HPCLauncher(
        backend="nccl"
    )

    runtime = launcher.launch()

    print("\nHPC Runtime Initialized:\n")

    print(
        json.dumps(
            runtime,
            indent=4,
        )
    )


# ================================================================
# PYTHON ENTRYPOINT
# ================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nHPC execution interrupted.\n"
        )

        sys.exit(1)

    except Exception as error:

        print(
            f"\nFatal HPC launcher failure: "
            f"{error}\n"
        )

        sys.exit(1)
