"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade HPC Runtime Management Infrastructure

Author:
    DARF HPC Systems Division

Purpose:
    Enterprise-grade runtime orchestration and execution
    environment management for:

        - Distributed AI training
        - Multi-node HPC execution
        - SLURM cluster orchestration
        - GPU resource coordination
        - Runtime metadata tracking
        - Elastic execution environments
        - Institutional reproducibility
        - Cluster-aware execution pipelines

Core Responsibilities:
    - runtime environment initialization
    - distributed execution metadata collection
    - cluster-aware runtime orchestration
    - hardware introspection
    - execution context validation
    - fault-tolerant runtime management
    - HPC-safe lifecycle control
    - runtime observability

Design Principles:
    - deterministic
    - fault-tolerant
    - HPC-compatible
    - distributed-safe
    - production-grade
    - institutionally reproducible
    - future extensible

Supported Execution Modes:
    - local CPU execution
    - single GPU
    - multi-GPU DDP
    - multi-node distributed HPC
    - SLURM orchestration
"""

import json
import os
import platform
import socket
import time
import traceback
from datetime import datetime

import psutil
import torch

from infrastructure.logging.structured_logger import (
    get_logger
)


class RuntimeManager:
    """
    Institutional-grade runtime orchestration manager.

    Handles:
        - runtime metadata collection
        - distributed execution introspection
        - hardware profiling
        - cluster-aware environment management
        - runtime validation
        - execution lifecycle monitoring
    """

    def __init__(
        self,
        enable_gpu_profiling=True,
        enable_system_profiling=True,
    ):

        self.enable_gpu_profiling = (
            enable_gpu_profiling
        )

        self.enable_system_profiling = (
            enable_system_profiling
        )

        self.logger = get_logger(
            name="RuntimeManager",
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
        # SLURM ENVIRONMENT
        # ========================================================

        self.slurm_job_id = os.environ.get(
            "SLURM_JOB_ID"
        )

        self.slurm_node_list = os.environ.get(
            "SLURM_NODELIST"
        )

        self.slurm_partition = os.environ.get(
            "SLURM_JOB_PARTITION"
        )

        self.slurm_num_nodes = os.environ.get(
            "SLURM_JOB_NUM_NODES"
        )

        # ========================================================
        # RUNTIME TIMESTAMP
        # ========================================================

        self.runtime_start_time = (
            time.time()
        )

        self.runtime_start_datetime = (
            datetime.utcnow().isoformat()
        )

    # ============================================================
    # MAIN METADATA COLLECTION
    # ============================================================

    def collect_runtime_metadata(self):
        """
        Collect complete runtime execution metadata.
        """

        metadata = {

            "execution":

                self._collect_execution_metadata(),

            "system":

                self._collect_system_metadata(),

            "distributed":

                self._collect_distributed_metadata(),

            "slurm":

                self._collect_slurm_metadata(),

            "hardware":

                self._collect_hardware_metadata(),

            "gpu":

                self._collect_gpu_metadata(),
        }

        self.logger.info(
            "Runtime metadata collection completed."
        )

        return metadata

    # ============================================================
    # EXECUTION METADATA
    # ============================================================

    def _collect_execution_metadata(self):

        return {

            "runtime_start_utc":
                self.runtime_start_datetime,

            "hostname":
                socket.gethostname(),

            "process_id":
                os.getpid(),

            "python_version":
                platform.python_version(),

            "platform":
                platform.platform(),

            "executable":
                os.path.abspath(__file__),
        }

    # ============================================================
    # SYSTEM METADATA
    # ============================================================

    def _collect_system_metadata(self):

        if not self.enable_system_profiling:

            return {}

        virtual_memory = psutil.virtual_memory()

        return {

            "cpu_count_logical":
                psutil.cpu_count(logical=True),

            "cpu_count_physical":
                psutil.cpu_count(logical=False),

            "cpu_percent":
                psutil.cpu_percent(interval=1),

            "memory_total_gb":
                round(
                    virtual_memory.total
                    / (1024 ** 3),
                    2,
                ),

            "memory_available_gb":
                round(
                    virtual_memory.available
                    / (1024 ** 3),
                    2,
                ),

            "memory_used_percent":
                virtual_memory.percent,

            "disk_usage_percent":
                psutil.disk_usage("/").percent,
        }

    # ============================================================
    # DISTRIBUTED METADATA
    # ============================================================

    def _collect_distributed_metadata(self):

        return {

            "rank":
                self.rank,

            "local_rank":
                self.local_rank,

            "world_size":
                self.world_size,

            "distributed_enabled":
                self.world_size > 1,
        }

    # ============================================================
    # SLURM METADATA
    # ============================================================

    def _collect_slurm_metadata(self):

        return {

            "slurm_enabled":
                self.slurm_job_id is not None,

            "job_id":
                self.slurm_job_id,

            "partition":
                self.slurm_partition,

            "node_list":
                self.slurm_node_list,

            "num_nodes":
                self.slurm_num_nodes,
        }

    # ============================================================
    # HARDWARE METADATA
    # ============================================================

    def _collect_hardware_metadata(self):

        return {

            "cuda_available":
                torch.cuda.is_available(),

            "gpu_count":
                (
                    torch.cuda.device_count()
                    if torch.cuda.is_available()
                    else 0
                ),

            "mps_available":
                torch.backends.mps.is_available()
                if hasattr(
                    torch.backends,
                    "mps"
                )
                else False,
        }

    # ============================================================
    # GPU METADATA
    # ============================================================

    def _collect_gpu_metadata(self):

        if (
            not torch.cuda.is_available()
            or not self.enable_gpu_profiling
        ):

            return {}

        gpu_data = []

        for gpu_id in range(
            torch.cuda.device_count()
        ):

            properties = (
                torch.cuda.get_device_properties(
                    gpu_id
                )
            )

            allocated_memory = round(
                torch.cuda.memory_allocated(gpu_id)
                / (1024 ** 3),
                3,
            )

            reserved_memory = round(
                torch.cuda.memory_reserved(gpu_id)
                / (1024 ** 3),
                3,
            )

            total_memory = round(
                properties.total_memory
                / (1024 ** 3),
                2,
            )

            gpu_data.append({

                "gpu_id":
                    gpu_id,

                "name":
                    properties.name,

                "total_memory_gb":
                    total_memory,

                "allocated_memory_gb":
                    allocated_memory,

                "reserved_memory_gb":
                    reserved_memory,

                "compute_capability":
                    (
                        f"{properties.major}."
                        f"{properties.minor}"
                    ),

                "multiprocessors":
                    properties.multi_processor_count,
            })

        return {

            "gpus": gpu_data
        }

    # ============================================================
    # RUNTIME VALIDATION
    # ============================================================

    def validate_runtime(self):
        """
        Validate runtime execution integrity.
        """

        self.logger.info(
            "Validating runtime environment."
        )

        if torch.cuda.is_available():

            gpu_count = (
                torch.cuda.device_count()
            )

            if self.local_rank >= gpu_count:

                raise RuntimeError(
                    f"Invalid LOCAL_RANK={self.local_rank}. "
                    f"Available GPUs={gpu_count}"
                )

        self.logger.info(
            "Runtime validation completed successfully."
        )

        return True

    # ============================================================
    # MEMORY SNAPSHOT
    # ============================================================

    def get_memory_snapshot(self):
        """
        Retrieve runtime memory snapshot.
        """

        snapshot = {

            "cpu_memory_percent":
                psutil.virtual_memory().percent,

            "cpu_memory_available_gb":
                round(
                    psutil.virtual_memory().available
                    / (1024 ** 3),
                    2,
                )
        }

        if torch.cuda.is_available():

            snapshot["gpu_memory_allocated_gb"] = (
                round(
                    torch.cuda.memory_allocated()
                    / (1024 ** 3),
                    3,
                )
            )

            snapshot["gpu_memory_reserved_gb"] = (
                round(
                    torch.cuda.memory_reserved()
                    / (1024 ** 3),
                    3,
                )
            )

        return snapshot

    # ============================================================
    # EXPORT RUNTIME REPORT
    # ============================================================

    def export_runtime_report(
        self,
        output_path=None,
    ):
        """
        Export runtime metadata to JSON.
        """

        metadata = (
            self.collect_runtime_metadata()
        )

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
                    metadata,
                    file,
                    indent=4,
                )

            self.logger.info(
                f"Runtime report exported: "
                f"{output_path}"
            )

        return metadata

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self):
        """
        Runtime cleanup.
        """

        try:

            if torch.cuda.is_available():

                torch.cuda.empty_cache()

            self.logger.info(
                "Runtime cleanup completed."
            )

        except Exception as error:

            self.logger.error(
                f"Runtime cleanup failed: "
                f"{error}"
            )

    # ============================================================
    # SAFE EXECUTION WRAPPER
    # ============================================================

    def safe_collect_runtime_metadata(self):
        """
        Fault-tolerant runtime metadata collection.
        """

        try:

            return (
                self.collect_runtime_metadata()
            )

        except Exception as error:

            self.logger.error(
                f"Runtime metadata collection failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"RuntimeManager("
            f"rank={self.rank}, "
            f"world_size={self.world_size}, "
            f"cuda={torch.cuda.is_available()})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    runtime = RuntimeManager()

    runtime.validate_runtime()

    metadata = (
        runtime.collect_runtime_metadata()
    )

    print("\nRuntime Metadata:\n")

    print(
        json.dumps(
            metadata,
            indent=4,
        )
    )
