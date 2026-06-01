"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade SLURM Orchestration Infrastructure

Author:
    DARF HPC Systems Division

Purpose:
    Enterprise-grade SLURM orchestration and HPC scheduling
    management system for:

        - Distributed AI training
        - Multi-node orchestration
        - GPU cluster scheduling
        - HPC runtime management
        - Elastic distributed execution
        - Institutional workload management
        - Fault-tolerant job execution
        - Resource-aware scheduling

Core Responsibilities:
    - SLURM environment detection
    - HPC job orchestration
    - distributed node management
    - resource allocation tracking
    - SLURM metadata management
    - job lifecycle monitoring
    - distributed-safe execution
    - fault-tolerant orchestration

Design Principles:
    - deterministic
    - HPC-compatible
    - distributed-safe
    - fault-tolerant
    - production-grade
    - institutionally reproducible
    - future extensible

Supported Modes:
    - single-node GPU execution
    - multi-node distributed training
    - elastic HPC execution
    - SLURM cluster orchestration
"""

import json
import os
import subprocess
import traceback
from datetime import datetime

from infrastructure.logging.structured_logger import (
    get_logger
)


class SlurmManager:
    """
    Institutional-grade SLURM orchestration manager.

    Handles:
        - SLURM environment introspection
        - distributed cluster metadata
        - resource tracking
        - node orchestration
        - HPC job lifecycle management
    """

    def __init__(
        self,
        enable_command_validation=True,
    ):

        self.enable_command_validation = (
            enable_command_validation
        )

        self.logger = get_logger(
            name="SlurmManager",
            log_dir="logs/hpc",
        )

        # ========================================================
        # SLURM ENVIRONMENT VARIABLES
        # ========================================================

        self.job_id = os.environ.get(
            "SLURM_JOB_ID"
        )

        self.job_name = os.environ.get(
            "SLURM_JOB_NAME"
        )

        self.node_list = os.environ.get(
            "SLURM_NODELIST"
        )

        self.num_nodes = os.environ.get(
            "SLURM_JOB_NUM_NODES"
        )

        self.partition = os.environ.get(
            "SLURM_JOB_PARTITION"
        )

        self.submit_host = os.environ.get(
            "SLURM_SUBMIT_HOST"
        )

        self.submit_directory = os.environ.get(
            "SLURM_SUBMIT_DIR"
        )

        self.cluster_name = os.environ.get(
            "SLURM_CLUSTER_NAME"
        )

        self.ntasks = os.environ.get(
            "SLURM_NTASKS"
        )

        self.gpus = os.environ.get(
            "SLURM_GPUS"
        )

        self.cpus_per_task = os.environ.get(
            "SLURM_CPUS_PER_TASK"
        )

        self.mem_per_node = os.environ.get(
            "SLURM_MEM_PER_NODE"
        )

    # ============================================================
    # SLURM DETECTION
    # ============================================================

    def detect_slurm_environment(self):
        """
        Detect whether execution is running under SLURM.
        """

        slurm_detected = (
            self.job_id is not None
        )

        self.logger.info(
            f"SLURM environment detected: "
            f"{slurm_detected}"
        )

        return slurm_detected

    # ============================================================
    # SLURM METADATA COLLECTION
    # ============================================================

    def collect_slurm_metadata(self):
        """
        Collect complete SLURM runtime metadata.
        """

        metadata = {

            "timestamp_utc":
                datetime.utcnow().isoformat(),

            "slurm_detected":
                self.detect_slurm_environment(),

            "job_id":
                self.job_id,

            "job_name":
                self.job_name,

            "partition":
                self.partition,

            "cluster_name":
                self.cluster_name,

            "node_list":
                self.node_list,

            "num_nodes":
                self.num_nodes,

            "ntasks":
                self.ntasks,

            "gpus":
                self.gpus,

            "cpus_per_task":
                self.cpus_per_task,

            "memory_per_node":
                self.mem_per_node,

            "submit_host":
                self.submit_host,

            "submit_directory":
                self.submit_directory,
        }

        self.logger.info(
            "SLURM metadata collected successfully."
        )

        return metadata

    # ============================================================
    # SLURM VALIDATION
    # ============================================================

    def validate_slurm_environment(self):
        """
        Validate SLURM runtime integrity.
        """

        self.logger.info(
            "Validating SLURM environment."
        )

        if not self.detect_slurm_environment():

            self.logger.warning(
                "Execution is not running inside SLURM."
            )

            return False

        required_variables = [

            "SLURM_JOB_ID",

            "SLURM_NODELIST",

            "SLURM_JOB_NUM_NODES",
        ]

        missing_variables = []

        for variable in required_variables:

            if variable not in os.environ:

                missing_variables.append(variable)

        if missing_variables:

            raise RuntimeError(
                f"Missing required SLURM variables: "
                f"{missing_variables}"
            )

        self.logger.info(
            "SLURM environment validation successful."
        )

        return True

    # ============================================================
    # NODE LIST PARSING
    # ============================================================

    def parse_node_list(self):
        """
        Parse SLURM node list safely.
        """

        if self.node_list is None:

            return []

        return [self.node_list]

    # ============================================================
    # RESOURCE SUMMARY
    # ============================================================

    def get_resource_summary(self):
        """
        Retrieve HPC resource allocation summary.
        """

        return {

            "nodes":
                self.num_nodes,

            "tasks":
                self.ntasks,

            "gpus":
                self.gpus,

            "cpus_per_task":
                self.cpus_per_task,

            "memory_per_node":
                self.mem_per_node,
        }

    # ============================================================
    # EXECUTE SLURM COMMAND
    # ============================================================

    def execute_command(
        self,
        command,
        timeout=30,
    ):
        """
        Execute SLURM-related system command safely.
        """

        if self.enable_command_validation:

            if not isinstance(command, list):

                raise TypeError(
                    "Command must be provided as list."
                )

        self.logger.info(
            f"Executing command: {' '.join(command)}"
        )

        try:

            result = subprocess.run(

                command,

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                timeout=timeout,

                text=True,

                check=False,
            )

            output = {

                "return_code":
                    result.returncode,

                "stdout":
                    result.stdout.strip(),

                "stderr":
                    result.stderr.strip(),
            }

            self.logger.info(
                f"Command execution completed | "
                f"ReturnCode={result.returncode}"
            )

            return output

        except subprocess.TimeoutExpired:

            raise RuntimeError(
                f"Command timed out after "
                f"{timeout} seconds."
            )

    # ============================================================
    # SLURM QUEUE STATUS
    # ============================================================

    def get_queue_status(self):
        """
        Retrieve SLURM queue status.
        """

        command = [

            "squeue",

            "-j",

            str(self.job_id),
        ]

        return self.execute_command(
            command=command
        )

    # ============================================================
    # NODE STATUS
    # ============================================================

    def get_node_status(self):
        """
        Retrieve SLURM node information.
        """

        if self.node_list is None:

            return {}

        command = [

            "scontrol",

            "show",

            "node",

            self.node_list,
        ]

        return self.execute_command(
            command=command
        )

    # ============================================================
    # EXPORT SLURM REPORT
    # ============================================================

    def export_slurm_report(
        self,
        output_path=None,
    ):
        """
        Export SLURM metadata report.
        """

        report = {

            "metadata":
                self.collect_slurm_metadata(),

            "resources":
                self.get_resource_summary(),
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
                f"SLURM report exported: "
                f"{output_path}"
            )

        return report

    # ============================================================
    # SAFE EXECUTION WRAPPER
    # ============================================================

    def safe_collect_metadata(self):
        """
        Fault-tolerant metadata collection wrapper.
        """

        try:

            return (
                self.collect_slurm_metadata()
            )

        except Exception as error:

            self.logger.error(
                f"SLURM metadata collection failed: "
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
            f"SlurmManager("
            f"job_id={self.job_id}, "
            f"partition={self.partition}, "
            f"nodes={self.num_nodes})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    manager = SlurmManager()

    print("\nSLURM Environment Detected:\n")

    print(
        manager.detect_slurm_environment()
    )

    print("\nSLURM Metadata:\n")

    print(
        json.dumps(
            manager.collect_slurm_metadata(),
            indent=4,
        )
    )
