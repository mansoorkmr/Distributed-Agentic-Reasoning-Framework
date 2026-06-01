"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Base Training Infrastructure

Author:
    DARF Training Infrastructure Division

Purpose:
    Production-grade training lifecycle engine supporting:

        - distributed training
        - mixed precision
        - fault-tolerant execution
        - checkpoint recovery
        - experiment lineage
        - evaluation hooks
        - gradient stability
        - institutional reproducibility

Core Features:
    - modular trainer abstraction
    - distributed-safe lifecycle
    - AMP mixed precision
    - gradient accumulation
    - gradient clipping
    - checkpoint integration
    - experiment tracking
    - structured logging
    - state lifecycle management
    - validation/evaluation hooks
    - automatic recovery readiness

Design Principles:
    - deterministic
    - scalable
    - distributed-safe
    - HPC-compatible
    - fault-tolerant
    - research reproducible
    - production-grade reliability
"""

import time
from pathlib import Path

import torch
from torch.cuda.amp import autocast, GradScaler

from infrastructure.logging.structured_logger import get_logger

from training.trainer.state_manager import (
    StateManager,
    TrainingState
)

from training.trainer.checkpoint_manager import (
    CheckpointManager
)

from training.trainer.experiment_manager import (
    ExperimentManager
)


class BaseTrainer:
    """
    Institutional-grade training lifecycle engine.

    Handles:
        - lifecycle orchestration
        - distributed-safe training
        - AMP execution
        - checkpointing
        - validation
        - experiment lineage
        - recovery readiness
    """

    def __init__(
        self,
        model,
        optimizer,
        criterion,
        train_loader,
        val_loader=None,
        scheduler=None,
        config=None,
        device=None
    ):

        # =========================================================
        # CORE OBJECTS
        # =========================================================

        self.model = model

        self.optimizer = optimizer

        self.criterion = criterion

        self.train_loader = train_loader

        self.val_loader = val_loader

        self.scheduler = scheduler

        self.config = config or {}

        # =========================================================
        # DEVICE
        # =========================================================

        self.device = device or (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model.to(self.device)

        # =========================================================
        # LOGGER
        # =========================================================

        self.logger = get_logger(
            name="BaseTrainer",
            log_dir="logs/training"
        )

        # =========================================================
        # STATE MANAGEMENT
        # =========================================================

        self.state_manager = StateManager()

        # =========================================================
        # CHECKPOINT MANAGER
        # =========================================================

        self.checkpoint_manager = (
            CheckpointManager()
        )

        # =========================================================
        # EXPERIMENT MANAGER
        # =========================================================

        self.experiment_manager = (
            ExperimentManager()
        )

        # =========================================================
        # TRAINING CONFIGURATION
        # =========================================================

        self.epochs = self.config.get(
            "epochs",
            10
        )

        self.gradient_accumulation_steps = (
            self.config.get(
                "gradient_accumulation_steps",
                1
            )
        )

        self.max_grad_norm = self.config.get(
            "max_grad_norm",
            1.0
        )

        self.use_amp = self.config.get(
            "use_amp",
            True
        )

        self.log_interval = self.config.get(
            "log_interval",
            10
        )

        self.checkpoint_interval = (
            self.config.get(
                "checkpoint_interval",
                1
            )
        )

        # =========================================================
        # MIXED PRECISION
        # =========================================================

        self.scaler = GradScaler(
            enabled=self.use_amp
        )

        # =========================================================
        # TRAINING STATE
        # =========================================================

        self.current_epoch = 0

        self.global_step = 0

        self.best_metric = float("inf")

        self.training_start_time = None

        # =========================================================
        # EXPERIMENT CREATION
        # =========================================================

        self.experiment = (
            self.experiment_manager.create_run(
                experiment_name="distributed_training",
                config=self.config
            )
        )

        self.run_id = self.experiment["run_id"]

        self.run_dir = self.experiment["run_dir"]

        self.logger.info(
            f"Experiment initialized: {self.run_id}"
        )

    # =============================================================
    # ENVIRONMENT VALIDATION
    # =============================================================

    def validate_environment(self):

        self.state_manager.transition(
            TrainingState.VALIDATING_ENVIRONMENT
        )

        self.logger.info(
            "Validating execution environment."
        )

        if not torch.cuda.is_available():

            self.logger.warning(
                "CUDA unavailable. "
                "Using CPU execution."
            )

        else:

            gpu_name = torch.cuda.get_device_name(0)

            self.logger.info(
                f"CUDA available: {gpu_name}"
            )

    # =============================================================
    # TRAIN ENTRYPOINT
    # =============================================================

    def train(self):

        try:

            self.validate_environment()

            self.state_manager.transition(
                TrainingState.TRAINING
            )

            self.training_start_time = time.time()

            self.logger.info(
                "Training lifecycle started."
            )

            for epoch in range(self.epochs):

                self.current_epoch = epoch

                train_loss = self.train_epoch()

                val_loss = None

                if self.val_loader:

                    val_loss = self.validate()

                # -------------------------------------------------
                # Scheduler Step
                # -------------------------------------------------

                if self.scheduler:

                    self.scheduler.step()

                # -------------------------------------------------
                # Checkpointing
                # -------------------------------------------------

                if (
                    epoch %
                    self.checkpoint_interval == 0
                ):

                    self.save_checkpoint(
                        train_loss=train_loss,
                        val_loss=val_loss
                    )

                # -------------------------------------------------
                # Best Model Tracking
                # -------------------------------------------------

                if (
                    val_loss is not None
                    and val_loss < self.best_metric
                ):

                    self.best_metric = val_loss

                    self.save_checkpoint(
                        train_loss=train_loss,
                        val_loss=val_loss,
                        is_best=True
                    )

            self.state_manager.transition(
                TrainingState.COMPLETED
            )

            self.logger.info(
                "Training completed successfully."
            )

        except Exception as e:

            self.state_manager.mark_failed(
                reason=str(e)
            )

            self.logger.exception(
                "Training lifecycle failed."
            )

            raise e

    # =============================================================
    # TRAIN SINGLE EPOCH
    # =============================================================

    def train_epoch(self):

        self.model.train()

        epoch_loss = 0.0

        total_batches = len(self.train_loader)

        self.logger.info(
            f"Epoch {self.current_epoch} started."
        )

        for batch_idx, batch in enumerate(
            self.train_loader
        ):

            inputs, targets = batch

            inputs = inputs.to(self.device)

            targets = targets.to(self.device)

            # -----------------------------------------------------
            # FORWARD PASS
            # -----------------------------------------------------

            with autocast(enabled=self.use_amp):

                outputs = self.model(inputs)

                loss = self.criterion(
                    outputs,
                    targets
                )

                loss = (
                    loss /
                    self.gradient_accumulation_steps
                )

            # -----------------------------------------------------
            # BACKWARD PASS
            # -----------------------------------------------------

            self.scaler.scale(loss).backward()

            # -----------------------------------------------------
            # OPTIMIZER STEP
            # -----------------------------------------------------

            if (
                (batch_idx + 1)
                %
                self.gradient_accumulation_steps
                == 0
            ):

                # ---------------------------------------------
                # Gradient Clipping
                # ---------------------------------------------

                self.scaler.unscale_(
                    self.optimizer
                )

                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.max_grad_norm
                )

                # ---------------------------------------------
                # Optimizer Step
                # ---------------------------------------------

                self.scaler.step(
                    self.optimizer
                )

                self.scaler.update()

                self.optimizer.zero_grad(
                    set_to_none=True
                )

            # -----------------------------------------------------
            # LOSS TRACKING
            # -----------------------------------------------------

            batch_loss = (
                loss.item()
                *
                self.gradient_accumulation_steps
            )

            epoch_loss += batch_loss

            self.global_step += 1

            # -----------------------------------------------------
            # LOGGING
            # -----------------------------------------------------

            if (
                batch_idx %
                self.log_interval
                == 0
            ):

                self.logger.info(
                    f"Epoch={self.current_epoch} | "
                    f"Batch={batch_idx}/{total_batches} | "
                    f"Loss={batch_loss:.6f}"
                )

        average_loss = (
            epoch_loss / total_batches
        )

        self.logger.info(
            f"Epoch {self.current_epoch} "
            f"completed. "
            f"Average Loss={average_loss:.6f}"
        )

        return average_loss

    # =============================================================
    # VALIDATION
    # =============================================================

    @torch.no_grad()
    def validate(self):

        self.state_manager.transition(
            TrainingState.VALIDATING
        )

        self.model.eval()

        validation_loss = 0.0

        total_batches = len(self.val_loader)

        self.logger.info(
            "Validation phase started."
        )

        for batch in self.val_loader:

            inputs, targets = batch

            inputs = inputs.to(self.device)

            targets = targets.to(self.device)

            with autocast(enabled=self.use_amp):

                outputs = self.model(inputs)

                loss = self.criterion(
                    outputs,
                    targets
                )

            validation_loss += loss.item()

        average_validation_loss = (
            validation_loss / total_batches
        )

        self.logger.info(
            f"Validation Loss="
            f"{average_validation_loss:.6f}"
        )

        self.state_manager.transition(
            TrainingState.TRAINING
        )

        return average_validation_loss

    # =============================================================
    # CHECKPOINT SAVE
    # =============================================================

    def save_checkpoint(
        self,
        train_loss,
        val_loss=None,
        is_best=False
    ):

        self.state_manager.transition(
            TrainingState.CHECKPOINTING
        )

        metrics = {

            "train_loss": train_loss,

            "val_loss": val_loss
        }

        checkpoint_path = (
            self.checkpoint_manager.save_checkpoint(
                model=self.model,
                optimizer=self.optimizer,
                scheduler=self.scheduler,
                scaler=self.scaler,
                epoch=self.current_epoch,
                global_step=self.global_step,
                loss=train_loss,
                metrics=metrics,
                is_best=is_best,
                metadata={
                    "run_id": self.run_id
                }
            )
        )

        self.logger.info(
            f"Checkpoint saved: "
            f"{checkpoint_path}"
        )

        self.state_manager.transition(
            TrainingState.TRAINING
        )

    # =============================================================
    # CHECKPOINT LOAD
    # =============================================================

    def resume_from_checkpoint(
        self,
        checkpoint_path
    ):

        self.logger.info(
            f"Restoring checkpoint: "
            f"{checkpoint_path}"
        )

        checkpoint = (
            self.checkpoint_manager.load_checkpoint(
                checkpoint_path=checkpoint_path,
                model=self.model,
                optimizer=self.optimizer,
                scheduler=self.scheduler,
                scaler=self.scaler
            )
        )

        self.current_epoch = (
            checkpoint["epoch"]
        )

        self.global_step = (
            checkpoint["global_step"]
        )

        self.logger.info(
            "Checkpoint restored successfully."
        )

    # =============================================================
    # EXPORT TRAINING SUMMARY
    # =============================================================

    def export_summary(self):

        training_time = (
            time.time()
            - self.training_start_time
        )

        summary = {

            "run_id": self.run_id,

            "epochs_completed":
                self.current_epoch,

            "global_steps":
                self.global_step,

            "best_metric":
                self.best_metric,

            "training_time_seconds":
                training_time,

            "device":
                self.device
        }

        summary_path = (
            Path(self.run_dir)
            / "training_summary.json"
        )

        import json

        with open(summary_path, "w") as f:

            json.dump(
                summary,
                f,
                indent=4
            )

        self.logger.info(
            f"Training summary exported: "
            f"{summary_path}"
        )

        return summary


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    from torch.utils.data import TensorDataset

    # ------------------------------------------------------------
    # Dummy Dataset
    # ------------------------------------------------------------

    X = torch.randn(1000, 10)

    y = torch.randint(0, 2, (1000,))

    dataset = TensorDataset(X, y)

    loader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True
    )

    # ------------------------------------------------------------
    # Dummy Model
    # ------------------------------------------------------------

    model = nn.Sequential(

        nn.Linear(10, 64),

        nn.ReLU(),

        nn.Linear(64, 2)
    )

    optimizer = optim.Adam(
        model.parameters(),
        lr=1e-3
    )

    criterion = nn.CrossEntropyLoss()

    # ------------------------------------------------------------
    # Trainer
    # ------------------------------------------------------------

    trainer = BaseTrainer(
        model=model,
        optimizer=optimizer,
        criterion=criterion,
        train_loader=loader,
        val_loader=loader,
        config={
            "epochs": 2,
            "use_amp": True,
            "gradient_accumulation_steps": 1
        }
    )

    trainer.train()

    trainer.export_summary()
