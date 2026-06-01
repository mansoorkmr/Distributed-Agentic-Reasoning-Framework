"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Experiment Management Infrastructure

Author:
    DARF Infrastructure Division

Purpose:
    Centralized experiment lifecycle management system
    for distributed training, orchestration, evaluation,
    reproducibility, lineage tracking, and HPC-safe execution.

Core Responsibilities:
    - Experiment registration
    - Run lineage tracking
    - Metadata persistence
    - Reproducibility guarantees
    - Artifact organization
    - Distributed-safe run creation
    - Recovery-aware experiment lifecycle
    - Institutional-grade auditability

Design Principles:
    - Fault tolerant
    - Deterministic
    - Distributed-safe
    - HPC-compatible
    - Resume-safe
    - Future extensible
"""

import os
import json
import uuid
import shutil
import hashlib
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from threading import Lock

from infrastructure.logging.structured_logger import get_logger


class ExperimentManager:
    """
    Institutional-grade experiment lifecycle manager.

    Handles:
        - run registration
        - metadata persistence
        - artifact lineage
        - experiment reproducibility
        - checkpoint lineage
        - audit-safe tracking
    """

    _lock = Lock()

    def __init__(
        self,
        base_dir: str = "experiments",
        registry_file: str = "experiment_index.json"
    ):

        self.logger = get_logger(
            name="ExperimentManager",
            log_dir="logs/system"
        )

        self.base_dir = Path(base_dir)

        self.registry_dir = self.base_dir / "registry"

        self.runs_dir = self.base_dir / "runs"

        self.templates_dir = self.base_dir / "templates"

        self.registry_file = self.registry_dir / registry_file

        self._initialize_directories()

        self._initialize_registry()

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def _initialize_directories(self):

        required_dirs = [
            self.base_dir,
            self.registry_dir,
            self.runs_dir,
            self.templates_dir
        ]

        for directory in required_dirs:

            directory.mkdir(parents=True, exist_ok=True)

    def _initialize_registry(self):

        if not self.registry_file.exists():

            with open(self.registry_file, "w") as f:
                json.dump([], f, indent=4)

    # ============================================================
    # EXPERIMENT CREATION
    # ============================================================

    def create_run(
        self,
        experiment_name: str,
        config: dict = None,
        tags: list = None,
        description: str = None
    ):

        """
        Create a fully tracked experiment run.

        Returns:
            dict containing:
                - run_id
                - run_dir
                - metadata
        """

        with self._lock:

            timestamp = datetime.utcnow().strftime(
                "%Y%m%d_%H%M%S"
            )

            unique_hash = uuid.uuid4().hex[:8]

            run_id = (
                f"{experiment_name}_"
                f"{timestamp}_"
                f"{unique_hash}"
            )

            run_dir = self.runs_dir / run_id

            self._create_run_structure(run_dir)

            metadata = self._build_metadata(
                run_id=run_id,
                experiment_name=experiment_name,
                config=config,
                tags=tags,
                description=description
            )

            self._write_metadata(run_dir, metadata)

            self._register_experiment(metadata)

            self.logger.info(
                f"Experiment created successfully: {run_id}"
            )

            return {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "metadata": metadata
            }

    # ============================================================
    # RUN STRUCTURE
    # ============================================================

    def _create_run_structure(self, run_dir: Path):

        """
        Create institutional-grade experiment hierarchy.
        """

        subdirs = [
            "logs",
            "checkpoints",
            "artifacts",
            "configs",
            "metrics",
            "profiling",
            "recovery",
            "exports"
        ]

        for subdir in subdirs:

            (run_dir / subdir).mkdir(
                parents=True,
                exist_ok=True
            )

    # ============================================================
    # METADATA GENERATION
    # ============================================================

    def _build_metadata(
        self,
        run_id,
        experiment_name,
        config,
        tags,
        description
    ):

        metadata = {

            # ----------------------------------------------------
            # Core Identity
            # ----------------------------------------------------

            "run_id": run_id,

            "experiment_name": experiment_name,

            "description": description,

            "tags": tags or [],

            # ----------------------------------------------------
            # Lifecycle
            # ----------------------------------------------------

            "status": "INITIALIZED",

            "created_at": datetime.utcnow().isoformat(),

            "last_updated": datetime.utcnow().isoformat(),

            # ----------------------------------------------------
            # Reproducibility
            # ----------------------------------------------------

            "git_commit": self._get_git_commit(),

            "config_hash": self._hash_config(config),

            # ----------------------------------------------------
            # Environment
            # ----------------------------------------------------

            "system_info": {

                "platform": platform.platform(),

                "python_version": platform.python_version(),

                "processor": platform.processor(),

                "hostname": platform.node()
            },

            # ----------------------------------------------------
            # Runtime
            # ----------------------------------------------------

            "training_state": {

                "epoch": 0,

                "global_step": 0,

                "best_metric": None
            },

            # ----------------------------------------------------
            # Config
            # ----------------------------------------------------

            "config": config or {}
        }

        return metadata

    # ============================================================
    # REGISTRY MANAGEMENT
    # ============================================================

    def _register_experiment(self, metadata):

        with open(self.registry_file, "r") as f:

            registry = json.load(f)

        registry.append(metadata)

        with open(self.registry_file, "w") as f:

            json.dump(
                registry,
                f,
                indent=4
            )

    # ============================================================
    # METADATA PERSISTENCE
    # ============================================================

    def _write_metadata(
        self,
        run_dir: Path,
        metadata: dict
    ):

        metadata_path = run_dir / "metadata.json"

        with open(metadata_path, "w") as f:

            json.dump(
                metadata,
                f,
                indent=4
            )

        # Save config separately
        config_path = run_dir / "configs" / "config.json"

        with open(config_path, "w") as f:

            json.dump(
                metadata.get("config", {}),
                f,
                indent=4
            )

    # ============================================================
    # STATUS MANAGEMENT
    # ============================================================

    def update_status(
        self,
        run_id: str,
        status: str
    ):

        registry = self._load_registry()

        updated = False

        for entry in registry:

            if entry["run_id"] == run_id:

                entry["status"] = status

                entry["last_updated"] = (
                    datetime.utcnow().isoformat()
                )

                updated = True

                break

        if not updated:

            raise ValueError(
                f"Run ID not found: {run_id}"
            )

        self._save_registry(registry)

        self.logger.info(
            f"Run status updated: "
            f"{run_id} -> {status}"
        )

    # ============================================================
    # REGISTRY HELPERS
    # ============================================================

    def _load_registry(self):

        with open(self.registry_file, "r") as f:

            return json.load(f)

    def _save_registry(self, registry):

        with open(self.registry_file, "w") as f:

            json.dump(
                registry,
                f,
                indent=4
            )

    # ============================================================
    # HASHING
    # ============================================================

    def _hash_config(self, config):

        if config is None:

            return None

        config_str = json.dumps(
            config,
            sort_keys=True
        )

        return hashlib.sha256(
            config_str.encode()
        ).hexdigest()

    # ============================================================
    # GIT VERSION TRACKING
    # ============================================================

    def _get_git_commit(self):

        try:

            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"]
            ).decode().strip()

            return commit

        except Exception:

            return "UNKNOWN"

    # ============================================================
    # QUERY UTILITIES
    # ============================================================

    def get_run(self, run_id):

        registry = self._load_registry()

        for entry in registry:

            if entry["run_id"] == run_id:

                return entry

        return None

    def list_runs(self):

        return self._load_registry()

    # ============================================================
    # ARTIFACT MANAGEMENT
    # ============================================================

    def register_artifact(
        self,
        run_id,
        artifact_path,
        artifact_type="generic"
    ):

        run_dir = self.runs_dir / run_id

        artifacts_file = (
            run_dir / "artifacts" / "artifacts.json"
        )

        artifacts = []

        if artifacts_file.exists():

            with open(artifacts_file, "r") as f:

                artifacts = json.load(f)

        artifact_entry = {

            "artifact_type": artifact_type,

            "artifact_path": artifact_path,

            "registered_at": datetime.utcnow().isoformat()
        }

        artifacts.append(artifact_entry)

        with open(artifacts_file, "w") as f:

            json.dump(
                artifacts,
                f,
                indent=4
            )

        self.logger.info(
            f"Artifact registered for run: {run_id}"
        )

    # ============================================================
    # CLEANUP
    # ============================================================

    def delete_run(self, run_id):

        run_dir = self.runs_dir / run_id

        if run_dir.exists():

            shutil.rmtree(run_dir)

        registry = self._load_registry()

        registry = [
            r for r in registry
            if r["run_id"] != run_id
        ]

        self._save_registry(registry)

        self.logger.warning(
            f"Run deleted: {run_id}"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    manager = ExperimentManager()

    experiment = manager.create_run(
        experiment_name="distributed_training",
        config={
            "batch_size": 32,
            "learning_rate": 1e-4,
            "epochs": 10
        },
        tags=["training", "distributed", "v100"],
        description="Institutional-grade training run."
    )

    print("\nExperiment Created:\n")

    print(json.dumps(
        experiment,
        indent=4
    ))
