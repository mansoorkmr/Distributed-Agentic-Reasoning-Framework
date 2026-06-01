"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade HPC Resource Profiling Infrastructure

Author:
    DARF HPC Systems Division

Purpose:
    Enterprise-grade hardware/resource profiling engine
    for:

        - Distributed AI workloads
        - Multi-GPU monitoring
        - HPC runtime analytics
        - Resource utilization tracking
        - Cluster observability
        - GPU/CPU memory diagnostics
        - Institutional workload profiling
        - Performance optimization pipelines

Core Responsibilities:
    - GPU profiling
    - CPU utilization monitoring
    - memory diagnostics
    - distributed runtime profiling
    - resource bottleneck detection
    - hardware telemetry
    - HPC observability
    - runtime analytics

Design Principles:
    - deterministic
    - fault-tolerant
    - production-grade
    - HPC-compatible
    - distributed-safe
    - institutionally reproducible
    - future extensible

Supported Profiling:
    - CPU metrics
    - RAM metrics
    - GPU metrics
    - CUDA memory tracking
    - multi-GPU profiling
    - distributed runtime analytics
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


class ResourceProfiler:
    """
    Institutional-grade HPC resource profiler.

    Handles:
        - hardware telemetry
        - GPU profiling
        - CPU monitoring
        - memory diagnostics
        - distributed runtime analytics
        - HPC observability
    """

    def __init__(
        self,
        enable_gpu_profiling=True,
        enable_cpu_profiling=True,
        enable_memory_profiling=True,
    ):

        self.enable_gpu_profiling = (
            enable_gpu_profiling
        )

        self.enable_cpu_profiling = (
            enable_cpu_profiling
        )

        self.enable_memory_profiling = (
            enable_memory_profiling
        )

        self.logger = get_logger(
            name="ResourceProfiler",
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

    # ============================================================
    # MAIN RESOURCE PROFILE
    # ============================================================

    def profile_system(self):
        """
        Collect complete system resource profile.
        """

        profile = {

            "timestamp_utc":
                datetime.utcnow().isoformat(),

            "system":
                self._profile_system_info(),

            "cpu":
                self._profile_cpu(),

            "memory":
                self._profile_memory(),

            "gpu":
                self._profile_gpu(),

            "distributed":
                self._profile_distributed_runtime(),
        }

        self.logger.info(
            "System resource profiling completed."
        )

        return profile

    # ============================================================
    # SYSTEM INFO
    # ============================================================

    def _profile_system_info(self):

        return {

            "hostname":
                socket.gethostname(),

            "platform":
                platform.platform(),

            "python_version":
                platform.python_version(),

            "process_id":
                os.getpid(),
        }

    # ============================================================
    # CPU PROFILING
    # ============================================================

    def _profile_cpu(self):

        if not self.enable_cpu_profiling:

            return {}

        cpu_freq = psutil.cpu_freq()

        return {

            "logical_cores":
                psutil.cpu_count(logical=True),

            "physical_cores":
                psutil.cpu_count(logical=False),

            "cpu_percent":
                psutil.cpu_percent(interval=1),

            "load_average":
                (
                    os.getloadavg()
                    if hasattr(os, "getloadavg")
                    else None
                ),

            "cpu_frequency_mhz":
                (
                    cpu_freq.current
                    if cpu_freq is not None
                    else None
                ),
        }

    # ============================================================
    # MEMORY PROFILING
    # ============================================================

    def _profile_memory(self):

        if not self.enable_memory_profiling:

            return {}

        virtual_memory = psutil.virtual_memory()

        swap_memory = psutil.swap_memory()

        return {

            "total_memory_gb":
                round(
                    virtual_memory.total
                    / (1024 ** 3),
                    2,
                ),

            "available_memory_gb":
                round(
                    virtual_memory.available
                    / (1024 ** 3),
                    2,
                ),

            "used_memory_gb":
                round(
                    virtual_memory.used
                    / (1024 ** 3),
                    2,
                ),

            "memory_utilization_percent":
                virtual_memory.percent,

            "swap_total_gb":
                round(
                    swap_memory.total
                    / (1024 ** 3),
                    2,
                ),

            "swap_used_percent":
                swap_memory.percent,
        }

    # ============================================================
    # GPU PROFILING
    # ============================================================

    def _profile_gpu(self):

        if (
            not self.enable_gpu_profiling
            or not torch.cuda.is_available()
        ):

            return {

                "cuda_available": False
            }

        gpu_profiles = []

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

            max_allocated = round(
                torch.cuda.max_memory_allocated(gpu_id)
                / (1024 ** 3),
                3,
            )

            total_memory = round(
                properties.total_memory
                / (1024 ** 3),
                2,
            )

            gpu_profiles.append({

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

                "max_allocated_memory_gb":
                    max_allocated,

                "free_memory_gb":
                    round(
                        total_memory
                        - reserved_memory,
                        3,
                    ),

                "multiprocessors":
                    properties.multi_processor_count,

                "compute_capability":
                    (
                        f"{properties.major}."
                        f"{properties.minor}"
                    ),

                "tensor_cores_supported":
                    properties.major >= 7,
            })

        return {

            "cuda_available": True,

            "gpu_count":
                torch.cuda.device_count(),

            "gpus":
                gpu_profiles,
        }

    # ============================================================
    # DISTRIBUTED PROFILING
    # ============================================================

    def _profile_distributed_runtime(self):

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
    # RUNTIME SNAPSHOT
    # ============================================================

    def runtime_snapshot(self):
        """
        Lightweight runtime telemetry snapshot.
        """

        snapshot = {

            "timestamp":
                time.time(),

            "cpu_percent":
                psutil.cpu_percent(),

            "memory_percent":
                psutil.virtual_memory().percent,
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
    # GPU MEMORY VALIDATION
    # ============================================================

    def validate_gpu_memory(
        self,
        threshold_percent=95.0,
    ):
        """
        Validate GPU memory safety thresholds.
        """

        if not torch.cuda.is_available():

            return True

        for gpu_id in range(
            torch.cuda.device_count()
        ):

            total_memory = (
                torch.cuda.get_device_properties(
                    gpu_id
                ).total_memory
            )

            reserved_memory = (
                torch.cuda.memory_reserved(gpu_id)
            )

            utilization = (
                reserved_memory / total_memory
            ) * 100.0

            if utilization >= threshold_percent:

                raise RuntimeError(
                    f"GPU memory threshold exceeded | "
                    f"GPU={gpu_id} | "
                    f"Utilization={utilization:.2f}%"
                )

        return True

    # ============================================================
    # MEMORY CLEANUP
    # ============================================================

    def cleanup_memory(self):
        """
        Cleanup GPU cache safely.
        """

        try:

            if torch.cuda.is_available():

                torch.cuda.empty_cache()

                torch.cuda.ipc_collect()

            self.logger.info(
                "GPU memory cleanup completed."
            )

        except Exception as error:

            self.logger.error(
                f"GPU cleanup failed: "
                f"{error}"
            )

    # ============================================================
    # EXPORT RESOURCE REPORT
    # ============================================================

    def export_profile(
        self,
        output_path=None,
    ):
        """
        Export profiling report to JSON.
        """

        profile = self.profile_system()

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
                    profile,
                    file,
                    indent=4,
                )

            self.logger.info(
                f"Resource profile exported: "
                f"{output_path}"
            )

        return profile

    # ============================================================
    # SAFE EXECUTION WRAPPER
    # ============================================================

    def safe_profile_system(self):
        """
        Fault-tolerant profiling wrapper.
        """

        try:

            return self.profile_system()

        except Exception as error:

            self.logger.error(
                f"Resource profiling failed: "
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
            f"ResourceProfiler("
            f"rank={self.rank}, "
            f"world_size={self.world_size}, "
            f"cuda={torch.cuda.is_available()})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    profiler = ResourceProfiler()

    profile = profiler.profile_system()

    print("\nSystem Resource Profile:\n")

    print(
        json.dumps(
            profile,
            indent=4,
        )
    )
