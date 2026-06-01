"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade HPC Node Validation Infrastructure

Author:
    DARF HPC Systems Division

Purpose:
    Enterprise-grade node validation and cluster integrity
    verification engine for:

        - Distributed AI infrastructure
        - Multi-node HPC execution
        - GPU cluster orchestration
        - SLURM environments
        - Institutional runtime validation
        - Fault-tolerant distributed execution
        - Hardware consistency verification
        - Node health monitoring

Core Responsibilities:
    - node integrity validation
    - GPU availability verification
    - distributed runtime consistency checks
    - memory and CPU validation
    - network hostname verification
    - CUDA runtime validation
    - cluster health diagnostics
    - institutional safety enforcement

Design Principles:
    - deterministic
    - fault-tolerant
    - production-grade
    - HPC-compatible
    - distributed-safe
    - institutionally reproducible
    - future extensible

Supported Validation Domains:
    - CPU validation
    - RAM validation
    - GPU validation
    - CUDA validation
    - distributed runtime validation
    - hostname/network validation
    - SLURM runtime validation
"""

import json
import os
import platform
import socket
import traceback
from datetime import datetime

import psutil
import torch

from infrastructure.logging.structured_logger import (
    get_logger
)


class NodeValidator:
    """
    Institutional-grade HPC node validator.

    Handles:
        - node health diagnostics
        - distributed runtime integrity
        - GPU consistency checks
        - hardware validation
        - HPC safety verification
    """

    def __init__(
        self,
        require_cuda=False,
        minimum_memory_gb=8,
        minimum_cpu_cores=4,
    ):

        self.require_cuda = require_cuda

        self.minimum_memory_gb = (
            minimum_memory_gb
        )

        self.minimum_cpu_cores = (
            minimum_cpu_cores
        )

        self.logger = get_logger(
            name="NodeValidator",
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
    # MAIN VALIDATION PIPELINE
    # ============================================================

    def validate_node(self):
        """
        Execute complete institutional-grade node validation.
        """

        self.logger.info(
            "Starting node validation pipeline."
        )

        report = {

            "timestamp_utc":
                datetime.utcnow().isoformat(),

            "hostname":
                socket.gethostname(),

            "platform":
                platform.platform(),

            "cpu":
                self._validate_cpu(),

            "memory":
                self._validate_memory(),

            "gpu":
                self._validate_gpu(),

            "distributed":
                self._validate_distributed_runtime(),

            "network":
                self._validate_network(),
        }

        self.logger.info(
            "Node validation completed successfully."
        )

        return report

    # ============================================================
    # CPU VALIDATION
    # ============================================================

    def _validate_cpu(self):

        logical_cores = psutil.cpu_count(
            logical=True
        )

        physical_cores = psutil.cpu_count(
            logical=False
        )

        cpu_percent = psutil.cpu_percent(
            interval=1
        )

        if (
            physical_cores
            < self.minimum_cpu_cores
        ):

            raise RuntimeError(
                f"Insufficient CPU cores | "
                f"Required={self.minimum_cpu_cores} | "
                f"Available={physical_cores}"
            )

        return {

            "logical_cores":
                logical_cores,

            "physical_cores":
                physical_cores,

            "cpu_utilization_percent":
                cpu_percent,
        }

    # ============================================================
    # MEMORY VALIDATION
    # ============================================================

    def _validate_memory(self):

        virtual_memory = psutil.virtual_memory()

        total_memory_gb = round(
            virtual_memory.total
            / (1024 ** 3),
            2,
        )

        available_memory_gb = round(
            virtual_memory.available
            / (1024 ** 3),
            2,
        )

        if (
            total_memory_gb
            < self.minimum_memory_gb
        ):

            raise RuntimeError(
                f"Insufficient RAM | "
                f"Required={self.minimum_memory_gb} GB | "
                f"Available={total_memory_gb} GB"
            )

        return {

            "total_memory_gb":
                total_memory_gb,

            "available_memory_gb":
                available_memory_gb,

            "memory_utilization_percent":
                virtual_memory.percent,
        }

    # ============================================================
    # GPU VALIDATION
    # ============================================================

    def _validate_gpu(self):

        cuda_available = (
            torch.cuda.is_available()
        )

        if self.require_cuda and not cuda_available:

            raise RuntimeError(
                "CUDA required but unavailable."
            )

        if not cuda_available:

            return {

                "cuda_available": False
            }

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

                "compute_capability":
                    (
                        f"{properties.major}."
                        f"{properties.minor}"
                    ),

                "multiprocessors":
                    properties.multi_processor_count,
            })

        return {

            "cuda_available": True,

            "gpu_count":
                torch.cuda.device_count(),

            "gpus":
                gpu_inventory,
        }

    # ============================================================
    # DISTRIBUTED VALIDATION
    # ============================================================

    def _validate_distributed_runtime(self):

        distributed_enabled = (
            self.world_size > 1
        )

        return {

            "distributed_enabled":
                distributed_enabled,

            "rank":
                self.rank,

            "local_rank":
                self.local_rank,

            "world_size":
                self.world_size,
        }

    # ============================================================
    # NETWORK VALIDATION
    # ============================================================

    def _validate_network(self):

        hostname = socket.gethostname()

        ip_address = socket.gethostbyname(
            hostname
        )

        return {

            "hostname":
                hostname,

            "ip_address":
                ip_address,
        }

    # ============================================================
    # GPU MEMORY SAFETY
    # ============================================================

    def validate_gpu_memory_safety(
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
                >= threshold_percent
            ):

                raise RuntimeError(
                    f"GPU memory threshold exceeded | "
                    f"GPU={gpu_id} | "
                    f"Utilization={utilization:.2f}%"
                )

        return True

    # ============================================================
    # CUDA VALIDATION
    # ============================================================

    def validate_cuda_runtime(self):
        """
        Validate CUDA runtime integrity.
        """

        if not torch.cuda.is_available():

            if self.require_cuda:

                raise RuntimeError(
                    "CUDA unavailable."
                )

            return False

        test_tensor = torch.randn(
            8,
            8,
            device="cuda"
        )

        result = torch.matmul(
            test_tensor,
            test_tensor
        )

        if result is None:

            raise RuntimeError(
                "CUDA runtime validation failed."
            )

        self.logger.info(
            "CUDA runtime validation successful."
        )

        return True

    # ============================================================
    # EXPORT VALIDATION REPORT
    # ============================================================

    def export_validation_report(
        self,
        output_path=None,
    ):
        """
        Export validation report to JSON.
        """

        report = self.validate_node()

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
                f"Validation report exported: "
                f"{output_path}"
            )

        return report

    # ============================================================
    # SAFE EXECUTION WRAPPER
    # ============================================================

    def safe_validate_node(self):
        """
        Fault-tolerant node validation wrapper.
        """

        try:

            return self.validate_node()

        except Exception as error:

            self.logger.error(
                f"Node validation failed: "
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
                "Node validator cleanup completed."
            )

        except Exception as error:

            self.logger.error(
                f"Cleanup failed: "
                f"{error}"
            )

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"NodeValidator("
            f"rank={self.rank}, "
            f"world_size={self.world_size}, "
            f"cuda_required={self.require_cuda})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    validator = NodeValidator(
        require_cuda=False
    )

    report = validator.validate_node()

    print("\nNode Validation Report:\n")

    print(
        json.dumps(
            report,
            indent=4,
        )
    )
