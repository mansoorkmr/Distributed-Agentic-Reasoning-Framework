"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade GPU Scheduling Infrastructure

Author:
    DARF HPC Systems Division

Purpose:
    Enterprise-grade GPU scheduling and allocation engine
    for:

        - Distributed AI workloads
        - Multi-GPU orchestration
        - HPC cluster scheduling
        - Resource-aware execution
        - Elastic distributed training
        - Institutional workload balancing
        - GPU allocation optimization
        - Runtime compute orchestration

Core Responsibilities:
    - GPU discovery
    - resource-aware scheduling
    - memory-aware allocation
    - distributed-safe device assignment
    - workload balancing
    - GPU utilization monitoring
    - compute capability validation
    - HPC scheduling orchestration

Design Principles:
    - deterministic
    - fault-tolerant
    - production-grade
    - HPC-compatible
    - distributed-safe
    - institutionally reproducible
    - future extensible

Supported Scheduling Policies:
    - least-utilized GPU
    - maximum-free-memory
    - round-robin allocation
    - capability-aware scheduling
    - rank-aware distributed assignment
"""

import json
import os
import traceback
from datetime import datetime

import torch

from infrastructure.logging.structured_logger import (
    get_logger
)


class GPUScheduler:
    """
    Institutional-grade GPU scheduling engine.

    Handles:
        - GPU resource orchestration
        - workload balancing
        - distributed-safe allocation
        - runtime GPU selection
        - HPC scheduling policies
    """

    SUPPORTED_POLICIES = {

        "max_free_memory",

        "round_robin",

        "rank_based",

        "least_reserved_memory",
    }

    def __init__(
        self,
        scheduling_policy="max_free_memory",
        memory_safety_margin_gb=2.0,
    ):

        self.scheduling_policy = (
            scheduling_policy
        )

        self.memory_safety_margin_gb = (
            memory_safety_margin_gb
        )

        self.logger = get_logger(
            name="GPUScheduler",
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

        self._validate_policy()

    # ============================================================
    # POLICY VALIDATION
    # ============================================================

    def _validate_policy(self):

        if (
            self.scheduling_policy
            not in self.SUPPORTED_POLICIES
        ):

            raise ValueError(
                f"Unsupported scheduling policy: "
                f"{self.scheduling_policy}"
            )

    # ============================================================
    # GPU DISCOVERY
    # ============================================================

    def discover_gpus(self):
        """
        Discover all available GPUs safely.
        """

        if not torch.cuda.is_available():

            self.logger.warning(
                "CUDA unavailable. No GPUs detected."
            )

            return []

        gpu_inventory = []

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

            free_memory = round(
                total_memory - reserved_memory,
                3,
            )

            gpu_inventory.append({

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

                "free_memory_gb":
                    free_memory,

                "compute_capability":
                    (
                        f"{properties.major}."
                        f"{properties.minor}"
                    ),

                "multiprocessors":
                    properties.multi_processor_count,
            })

        self.logger.info(
            f"Discovered {len(gpu_inventory)} GPU(s)."
        )

        return gpu_inventory

    # ============================================================
    # GPU VALIDATION
    # ============================================================

    def validate_gpu_resources(
        self,
        required_memory_gb=None,
    ):
        """
        Validate cluster GPU resources.
        """

        gpus = self.discover_gpus()

        if len(gpus) == 0:

            raise RuntimeError(
                "No GPUs available."
            )

        if required_memory_gb is not None:

            valid_gpus = []

            for gpu in gpus:

                if (
                    gpu["free_memory_gb"]
                    >= (
                        required_memory_gb
                        + self.memory_safety_margin_gb
                    )
                ):

                    valid_gpus.append(gpu)

            if len(valid_gpus) == 0:

                raise RuntimeError(
                    "No GPUs satisfy memory requirements."
                )

        self.logger.info(
            "GPU resource validation successful."
        )

        return True

    # ============================================================
    # GPU SELECTION
    # ============================================================

    def select_gpu(
        self,
        required_memory_gb=None,
    ):
        """
        Select GPU according to scheduling policy.
        """

        gpus = self.discover_gpus()

        if len(gpus) == 0:

            raise RuntimeError(
                "No GPUs available for scheduling."
            )

        # --------------------------------------------------------
        # FILTER MEMORY REQUIREMENTS
        # --------------------------------------------------------

        if required_memory_gb is not None:

            filtered = []

            for gpu in gpus:

                if (
                    gpu["free_memory_gb"]
                    >= (
                        required_memory_gb
                        + self.memory_safety_margin_gb
                    )
                ):

                    filtered.append(gpu)

            gpus = filtered

        if len(gpus) == 0:

            raise RuntimeError(
                "No GPUs satisfy allocation requirements."
            )

        # --------------------------------------------------------
        # POLICY: MAX FREE MEMORY
        # --------------------------------------------------------

        if (
            self.scheduling_policy
            == "max_free_memory"
        ):

            selected = max(

                gpus,

                key=lambda gpu:
                    gpu["free_memory_gb"]
            )

        # --------------------------------------------------------
        # POLICY: LEAST RESERVED MEMORY
        # --------------------------------------------------------

        elif (
            self.scheduling_policy
            == "least_reserved_memory"
        ):

            selected = min(

                gpus,

                key=lambda gpu:
                    gpu["reserved_memory_gb"]
            )

        # --------------------------------------------------------
        # POLICY: ROUND ROBIN
        # --------------------------------------------------------

        elif (
            self.scheduling_policy
            == "round_robin"
        ):

            index = (
                self.rank % len(gpus)
            )

            selected = gpus[index]

        # --------------------------------------------------------
        # POLICY: RANK BASED
        # --------------------------------------------------------

        elif (
            self.scheduling_policy
            == "rank_based"
        ):

            index = (
                self.local_rank % len(gpus)
            )

            selected = gpus[index]

        else:

            raise RuntimeError(
                "Unknown scheduling policy."
            )

        self.logger.info(
            f"Selected GPU={selected['gpu_id']} | "
            f"Policy={self.scheduling_policy}"
        )

        return selected

    # ============================================================
    # GPU ASSIGNMENT
    # ============================================================

    def assign_gpu(
        self,
        required_memory_gb=None,
    ):
        """
        Assign GPU and configure CUDA runtime.
        """

        selected_gpu = self.select_gpu(
            required_memory_gb=required_memory_gb
        )

        gpu_id = selected_gpu["gpu_id"]

        torch.cuda.set_device(gpu_id)

        self.logger.info(
            f"Assigned CUDA device: cuda:{gpu_id}"
        )

        return gpu_id

    # ============================================================
    # UTILIZATION SNAPSHOT
    # ============================================================

    def utilization_snapshot(self):
        """
        Lightweight GPU utilization snapshot.
        """

        snapshot = {

            "timestamp_utc":
                datetime.utcnow().isoformat(),

            "cuda_available":
                torch.cuda.is_available(),

            "gpu_count":
                (
                    torch.cuda.device_count()
                    if torch.cuda.is_available()
                    else 0
                ),

            "gpus":
                self.discover_gpus(),
        }

        return snapshot

    # ============================================================
    # MEMORY SAFETY VALIDATION
    # ============================================================

    def validate_memory_safety(
        self,
        utilization_threshold_percent=95.0,
    ):
        """
        Validate GPU memory safety thresholds.
        """

        if not torch.cuda.is_available():

            return True

        for gpu_id in range(
            torch.cuda.device_count()
        ):

            reserved_memory = (
                torch.cuda.memory_reserved(gpu_id)
            )

            total_memory = (
                torch.cuda.get_device_properties(
                    gpu_id
                ).total_memory
            )

            utilization = (
                reserved_memory
                / total_memory
            ) * 100.0

            if (
                utilization
                >= utilization_threshold_percent
            ):

                raise RuntimeError(
                    f"GPU memory threshold exceeded | "
                    f"GPU={gpu_id} | "
                    f"Utilization={utilization:.2f}%"
                )

        return True

    # ============================================================
    # EXPORT GPU REPORT
    # ============================================================

    def export_gpu_report(
        self,
        output_path=None,
    ):
        """
        Export GPU scheduling report.
        """

        report = {

            "policy":
                self.scheduling_policy,

            "distributed_rank":
                self.rank,

            "world_size":
                self.world_size,

            "gpu_inventory":
                self.discover_gpus(),
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
                f"GPU report exported: "
                f"{output_path}"
            )

        return report

    # ============================================================
    # SAFE EXECUTION WRAPPER
    # ============================================================

    def safe_assign_gpu(
        self,
        required_memory_gb=None,
    ):
        """
        Fault-tolerant GPU assignment wrapper.
        """

        try:

            return self.assign_gpu(
                required_memory_gb=required_memory_gb
            )

        except Exception as error:

            self.logger.error(
                f"GPU assignment failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self):
        """
        Cleanup GPU runtime safely.
        """

        try:

            if torch.cuda.is_available():

                torch.cuda.empty_cache()

                torch.cuda.ipc_collect()

            self.logger.info(
                "GPU scheduler cleanup completed."
            )

        except Exception as error:

            self.logger.error(
                f"GPU cleanup failed: "
                f"{error}"
            )

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"GPUScheduler("
            f"policy={self.scheduling_policy}, "
            f"rank={self.rank}, "
            f"world_size={self.world_size})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    scheduler = GPUScheduler(
        scheduling_policy="max_free_memory"
    )

    print("\nGPU Inventory:\n")

    print(
        json.dumps(
            scheduler.discover_gpus(),
            indent=4,
        )
    )

    if torch.cuda.is_available():

        selected_gpu = scheduler.select_gpu()

        print("\nSelected GPU:\n")

        print(
            json.dumps(
                selected_gpu,
                indent=4,
            )
        )
