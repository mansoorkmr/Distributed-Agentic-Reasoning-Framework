"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Checkpoint Management Infrastructure

Author:
    DARF Training Infrastructure Division

Purpose:
    Fault-tolerant, distributed-safe checkpoint lifecycle manager
    for training, recovery, reproducibility, and experiment lineage.

Core Responsibilities:
    - Atomic checkpoint saving
    - Distributed-safe checkpoint handling
    - Resume-safe restoration
    - Optimizer/scaler/scheduler persistence
    - RNG state persistence
    - Best-model tracking
    - Versioned checkpoint lineage
    - Recovery-safe restoration
    - HPC-compatible checkpointing

Design Principles:
    - Deterministic
    - Fault tolerant
    - Distributed-aware
    - Future extensible
    - Research reproducible
    - Production-grade resilience
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

import torch

from infrastructure.logging.structured_logger import get_logger


class CheckpointManager:
    """
    Institutional-grade checkpoint manager.

    Supports:
        - distributed training
        - mixed precision
        - resume-safe execution
        - atomic writes
        - experiment lineage
        - best checkpoint tracking
    """

    def __init__(
        self,
        checkpoint_root="training/checkpoints",
        max_to_keep=5,
        save_optimizer=True,
        save_scheduler=True,
        save_scaler=True,
        save_rng_state=True
    ):

        self.logger = get_logger(
            name="CheckpointManager",
            log_dir="logs/training"
        )

        self.checkpoint_root = Path(checkpoint_root)

        self.max_to_keep = max_to_keep

        self.save_optimizer = save_optimizer

        self.save_scheduler = save_scheduler

        self.save_scaler = save_scaler

        self.save_rng_state = save_rng_state

        self.latest_dir = self.checkpoint_root / "latest"

        self.best_dir = self.checkpoint_root / "best"

        self.archive_dir = self.checkpoint_root / "archive"

        self._initialize_directories()

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def _initialize_directories(self):

        required_dirs = [
            self.latest_dir,
            self.best_dir,
            self.archive_dir
        ]

        for directory in required_dirs:

            directory.mkdir(
                parents=True,
                exist_ok=True
            )

    # ============================================================
    # CHECKPOINT SAVE
    # ============================================================

    def save_checkpoint(
        self,
        model,
        epoch,
        global_step,
        loss,
        optimizer=None,
        scheduler=None,
        scaler=None,
        metrics=None,
        is_best=False,
        metadata=None,
        checkpoint_name=None
    ):

        """
        Save complete training checkpoint.

        Includes:
            - model weights
            - optimizer state
            - scheduler state
            - scaler state
            - RNG state
            - metrics
            - metadata
        """

        timestamp = datetime.utcnow().strftime(
            "%Y%m%d_%H%M%S"
        )

        if checkpoint_name is None:

            checkpoint_name = (
                f"checkpoint_epoch_{epoch}_"
                f"step_{global_step}_"
                f"{timestamp}.pt"
            )

        checkpoint_path = (
            self.latest_dir / checkpoint_name
        )

        checkpoint = {

            # ----------------------------------------------------
            # Core Training State
            # ----------------------------------------------------

            "epoch": epoch,

            "global_step": global_step,

            "loss": loss,

            # ----------------------------------------------------
            # Model
            # ----------------------------------------------------

            "model_state_dict":
                model.state_dict(),

            # ----------------------------------------------------
            # Metadata
            # ----------------------------------------------------

            "metrics": metrics or {},

            "metadata": metadata or {},

            "saved_at":
                datetime.utcnow().isoformat()
        }

        # --------------------------------------------------------
        # Optimizer
        # --------------------------------------------------------

        if self.save_optimizer and optimizer:

            checkpoint["optimizer_state_dict"] = (
                optimizer.state_dict()
            )

        # --------------------------------------------------------
        # Scheduler
        # --------------------------------------------------------

        if self.save_scheduler and scheduler:

            checkpoint["scheduler_state_dict"] = (
                scheduler.state_dict()
            )

        # --------------------------------------------------------
        # AMP Scaler
        # --------------------------------------------------------

        if self.save_scaler and scaler:

            checkpoint["scaler_state_dict"] = (
                scaler.state_dict()
            )

        # --------------------------------------------------------
        # RNG State
        # --------------------------------------------------------

        if self.save_rng_state:

            checkpoint["rng_state"] = (
                torch.get_rng_state()
            )

            if torch.cuda.is_available():

                checkpoint["cuda_rng_state"] = (
                    torch.cuda.get_rng_state_all()
                )

        # --------------------------------------------------------
        # Atomic Save
        # --------------------------------------------------------

        self._atomic_save(
            checkpoint,
            checkpoint_path
        )

        self.logger.info(
            f"Checkpoint saved: {checkpoint_path}"
        )

        # --------------------------------------------------------
        # Archive Copy
        # --------------------------------------------------------

        archive_path = (
            self.archive_dir / checkpoint_name
        )

        shutil.copy2(
            checkpoint_path,
            archive_path
        )

        # --------------------------------------------------------
        # Best Checkpoint
        # --------------------------------------------------------

        if is_best:

            best_path = (
                self.best_dir / "best_model.pt"
            )

            shutil.copy2(
                checkpoint_path,
                best_path
            )

            self.logger.info(
                "Best checkpoint updated."
            )

        # --------------------------------------------------------
        # Retention Policy
        # --------------------------------------------------------

        self._cleanup_old_checkpoints()

        return str(checkpoint_path)

    # ============================================================
    # CHECKPOINT LOAD
    # ============================================================

    def load_checkpoint(
        self,
        checkpoint_path,
        model,
        optimizer=None,
        scheduler=None,
        scaler=None,
        strict=True
    ):

        """
        Restore training state safely.
        """

        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.exists():

            raise FileNotFoundError(
                f"Checkpoint not found: "
                f"{checkpoint_path}"
            )

        self.logger.info(
            f"Loading checkpoint: {checkpoint_path}"
        )

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu"
        )

        # --------------------------------------------------------
        # Restore Model
        # --------------------------------------------------------

        model.load_state_dict(
            checkpoint["model_state_dict"],
            strict=strict
        )

        # --------------------------------------------------------
        # Restore Optimizer
        # --------------------------------------------------------

        if (
            optimizer
            and "optimizer_state_dict" in checkpoint
        ):

            optimizer.load_state_dict(
                checkpoint["optimizer_state_dict"]
            )

        # --------------------------------------------------------
        # Restore Scheduler
        # --------------------------------------------------------

        if (
            scheduler
            and "scheduler_state_dict" in checkpoint
        ):

            scheduler.load_state_dict(
                checkpoint["scheduler_state_dict"]
            )

        # --------------------------------------------------------
        # Restore AMP Scaler
        # --------------------------------------------------------

        if (
            scaler
            and "scaler_state_dict" in checkpoint
        ):

            scaler.load_state_dict(
                checkpoint["scaler_state_dict"]
            )

        # --------------------------------------------------------
        # Restore RNG
        # --------------------------------------------------------

        if "rng_state" in checkpoint:

            torch.set_rng_state(
                checkpoint["rng_state"]
            )

        if (
            torch.cuda.is_available()
            and "cuda_rng_state" in checkpoint
        ):

            torch.cuda.set_rng_state_all(
                checkpoint["cuda_rng_state"]
            )

        self.logger.info(
            "Checkpoint restored successfully."
        )

        return checkpoint

    # ============================================================
    # ATOMIC SAVE
    # ============================================================

    def _atomic_save(
        self,
        checkpoint,
        target_path
    ):

        """
        Atomic checkpoint save.

        Prevents:
            - corruption
            - interrupted writes
            - partial saves
        """

        target_path = Path(target_path)

        with tempfile.NamedTemporaryFile(
            delete=False,
            dir=target_path.parent
        ) as tmp_file:

            temp_path = tmp_file.name

        try:

            torch.save(
                checkpoint,
                temp_path
            )

            os.replace(
                temp_path,
                target_path
            )

        except Exception as e:

            if os.path.exists(temp_path):

                os.remove(temp_path)

            self.logger.exception(
                "Atomic checkpoint save failed."
            )

            raise e

    # ============================================================
    # RETENTION MANAGEMENT
    # ============================================================

    def _cleanup_old_checkpoints(self):

        checkpoints = sorted(
            self.latest_dir.glob("*.pt"),
            key=os.path.getmtime
        )

        while len(checkpoints) > self.max_to_keep:

            oldest = checkpoints.pop(0)

            try:

                oldest.unlink()

                self.logger.warning(
                    f"Removed old checkpoint: {oldest}"
                )

            except Exception:

                self.logger.exception(
                    "Failed removing old checkpoint."
                )

    # ============================================================
    # LATEST CHECKPOINT
    # ============================================================

    def get_latest_checkpoint(self):

        checkpoints = sorted(
            self.latest_dir.glob("*.pt"),
            key=os.path.getmtime
        )

        if not checkpoints:

            return None

        return str(checkpoints[-1])

    # ============================================================
    # BEST CHECKPOINT
    # ============================================================

    def get_best_checkpoint(self):

        best_path = (
            self.best_dir / "best_model.pt"
        )

        if best_path.exists():

            return str(best_path)

        return None

    # ============================================================
    # CHECKPOINT VALIDATION
    # ============================================================

    def validate_checkpoint(
        self,
        checkpoint_path
    ):

        """
        Validate checkpoint integrity.
        """

        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.exists():

            return False

        try:

            checkpoint = torch.load(
                checkpoint_path,
                map_location="cpu"
            )

            required_keys = [

                "epoch",

                "global_step",

                "loss",

                "model_state_dict"
            ]

            for key in required_keys:

                if key not in checkpoint:

                    return False

            return True

        except Exception:

            self.logger.exception(
                "Checkpoint validation failed."
            )

            return False

    # ============================================================
    # EXPORT CHECKPOINT METADATA
    # ============================================================

    def export_checkpoint_metadata(
        self,
        checkpoint_path
    ):

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu"
        )

        metadata = {

            "epoch":
                checkpoint.get("epoch"),

            "global_step":
                checkpoint.get("global_step"),

            "loss":
                checkpoint.get("loss"),

            "saved_at":
                checkpoint.get("saved_at"),

            "metrics":
                checkpoint.get("metrics", {})
        }

        metadata_path = (
            Path(checkpoint_path).with_suffix(".json")
        )

        with open(metadata_path, "w") as f:

            json.dump(
                metadata,
                f,
                indent=4
            )

        self.logger.info(
            f"Checkpoint metadata exported: "
            f"{metadata_path}"
        )

    # ============================================================
    # SAFE DELETE
    # ============================================================

    def delete_checkpoint(
        self,
        checkpoint_path
    ):

        checkpoint_path = Path(checkpoint_path)

        if checkpoint_path.exists():

            checkpoint_path.unlink()

            self.logger.warning(
                f"Checkpoint deleted: "
                f"{checkpoint_path}"
            )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    import torch.nn as nn
    import torch.optim as optim

    model = nn.Linear(10, 2)

    optimizer = optim.Adam(
        model.parameters(),
        lr=1e-4
    )

    manager = CheckpointManager()

    path = manager.save_checkpoint(
        model=model,
        optimizer=optimizer,
        epoch=1,
        global_step=100,
        loss=0.1234,
        metrics={
            "accuracy": 0.91
        },
        is_best=True
    )

    print(f"\nCheckpoint Saved:\n{path}\n")

    checkpoint = manager.load_checkpoint(
        checkpoint_path=path,
        model=model,
        optimizer=optimizer
    )

    print(
        f"Restored Epoch: "
        f"{checkpoint['epoch']}"
    )
