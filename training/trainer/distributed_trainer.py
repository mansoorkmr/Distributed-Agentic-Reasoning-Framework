"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Distributed Training Engine

Author:
    DARF Distributed Systems Division

Purpose:
    Enterprise-grade distributed training orchestration engine
    supporting:

        - Distributed Data Parallel (DDP)
        - multi-GPU execution
        - mixed precision training
        - synchronized metric aggregation
        - distributed-safe checkpointing
        - fault-tolerant recovery
        - HPC execution environments
        - scalable institutional AI workloads

Core Responsibilities:
    - distributed lifecycle orchestration
    - DDP wrapping and synchronization
    - AMP mixed precision execution
    - distributed-safe validation
    - synchronized metric reduction
    - rank-aware checkpointing
    - distributed gradient stability
    - HPC-compatible execution

Design Principles:
    - deterministic
    - fault-tolerant
    - distributed-safe
    - HPC-compatible
    - production-grade
    - future extensible
    - institutionally reproducible

Supported Execution Modes:
    - single-node multi-GPU
    - multi-node distributed training
    - elastic distributed execution
"""

import time
import traceback

import torch
import torch.distributed as dist

from torch.cuda.amp import autocast
from torch.nn.parallel import (
    DistributedDataParallel as DDP
)

from training.trainer.base_trainer import (
    BaseTrainer
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

from training.distributed.ddp.synchronization.metric_reducer import (
    MetricReducer
)

from training.trainer.state_manager import (
    TrainingState
)

from infrastructure.logging.structured_logger import (
    get_logger
)


class DistributedTrainer(BaseTrainer):
    """
    Institutional-grade distributed training engine.

    Handles:
        - DDP lifecycle orchestration
        - multi-GPU execution
        - synchronized training
        - distributed-safe validation
        - mixed precision execution
        - fault-tolerant distributed training
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
        backend="nccl",
    ):

        # ========================================================
        # LOGGER
        # ========================================================

        self.logger = get_logger(
            name="DistributedTrainer",
            log_dir="logs/training",
        )

        # ========================================================
        # DISTRIBUTED COMPONENTS
        # ========================================================

        self.backend = backend

        self.device_manager = DeviceManager()

        self.validator = DistributedValidator(
            backend=backend
        )

        self.process_group_manager = (
            ProcessGroupManager(
                backend=backend
            )
        )

        self.metric_reducer = (
            MetricReducer()
        )

        # ========================================================
        # VALIDATE ENVIRONMENT
        # ========================================================

        self.validator.validate_environment()

        # ========================================================
        # INITIALIZE PROCESS GROUP
        # ========================================================

        self.process_group_manager.initialize()

        # ========================================================
        # INITIALIZE DEVICE
        # ========================================================

        self.device = (
            self.device_manager.initialize_device()
        )

        self.rank = (
            self.process_group_manager.get_rank()
        )

        self.local_rank = (
            self.process_group_manager.get_local_rank()
        )

        self.world_size = (
            self.process_group_manager.get_world_size()
        )

        # ========================================================
        # BASE TRAINER INITIALIZATION
        # ========================================================

        super().__init__(
            model=model,
            optimizer=optimizer,
            criterion=criterion,
            train_loader=train_loader,
            val_loader=val_loader,
            scheduler=scheduler,
            config=config,
            device=self.device,
        )

        # ========================================================
        # DISTRIBUTED MODEL WRAPPING
        # ========================================================

        self.model = DDP(

            self.model,

            device_ids=[self.local_rank]
            if torch.cuda.is_available()
            else None,

            output_device=self.local_rank
            if torch.cuda.is_available()
            else None,

            broadcast_buffers=True,

            find_unused_parameters=False,

            gradient_as_bucket_view=True,

            static_graph=False,
        )

        # ========================================================
        # DISTRIBUTED CONFIGURATION
        # ========================================================

        self.sync_validation_metrics = (
            self.config.get(
                "sync_validation_metrics",
                True,
            )
        )

        self.distributed_checkpointing = (
            self.config.get(
                "distributed_checkpointing",
                True,
            )
        )

        # ========================================================
        # INITIALIZATION LOGGING
        # ========================================================

        self.rank_zero_log(
            f"DistributedTrainer initialized | "
            f"Backend={self.backend} | "
            f"WorldSize={self.world_size}"
        )

    # ============================================================
    # RANK-AWARE LOGGING
    # ============================================================

    def rank_zero_log(
        self,
        message
    ):
        """
        Log only on main process.
        """

        if self.rank == 0:

            self.logger.info(message)

    # ============================================================
    # DISTRIBUTED TRAINING ENTRYPOINT
    # ============================================================

    def train(self):

        try:

            self.state_manager.transition(
                TrainingState.TRAINING
            )

            self.rank_zero_log(
                "Distributed training started."
            )

            self.training_start_time = (
                time.time()
            )

            for epoch in range(self.epochs):

                self.current_epoch = epoch

                # -----------------------------------------------
                # DISTRIBUTED SAMPLER SYNCHRONIZATION
                # -----------------------------------------------

                if hasattr(
                    self.train_loader,
                    "sampler"
                ):

                    if hasattr(
                        self.train_loader.sampler,
                        "set_epoch"
                    ):

                        self.train_loader.sampler.set_epoch(
                            epoch
                        )

                # -----------------------------------------------
                # TRAIN EPOCH
                # -----------------------------------------------

                train_loss = self.train_epoch()

                # -----------------------------------------------
                # VALIDATION
                # -----------------------------------------------

                val_loss = None

                if self.val_loader:

                    val_loss = self.validate()

                # -----------------------------------------------
                # SCHEDULER STEP
                # -----------------------------------------------

                if self.scheduler:

                    self.scheduler.step()

                # -----------------------------------------------
                # CHECKPOINTING
                # -----------------------------------------------

                if self.rank == 0:

                    self.save_checkpoint(
                        train_loss=train_loss,
                        val_loss=val_loss,
                        is_best=(
                            val_loss is not None
                            and val_loss < self.best_metric
                        )
                    )

                # -----------------------------------------------
                # BEST MODEL TRACKING
                # -----------------------------------------------

                if (
                    val_loss is not None
                    and val_loss < self.best_metric
                ):

                    self.best_metric = val_loss

                # -----------------------------------------------
                # SYNCHRONIZATION
                # -----------------------------------------------

                self.metric_reducer.barrier()

            self.state_manager.transition(
                TrainingState.COMPLETED
            )

            self.rank_zero_log(
                "Distributed training completed successfully."
            )

        except Exception as error:

            self.state_manager.mark_failed(
                reason=str(error)
            )

            self.logger.error(
                f"Distributed training failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

        finally:

            self.cleanup()

    # ============================================================
    # DISTRIBUTED TRAIN EPOCH
    # ============================================================

    def train_epoch(self):

        self.model.train()

        epoch_loss = 0.0

        total_batches = len(
            self.train_loader
        )

        self.rank_zero_log(
            f"Epoch {self.current_epoch} started."
        )

        for batch_idx, batch in enumerate(
            self.train_loader
        ):

            inputs, targets = batch

            inputs = inputs.to(
                self.device,
                non_blocking=True
            )

            targets = targets.to(
                self.device,
                non_blocking=True
            )

            # ---------------------------------------------------
            # FORWARD PASS
            # ---------------------------------------------------

            with autocast(
                enabled=self.use_amp
            ):

                outputs = self.model(inputs)

                loss = self.criterion(
                    outputs,
                    targets
                )

                loss = (
                    loss /
                    self.gradient_accumulation_steps
                )

            # ---------------------------------------------------
            # BACKWARD PASS
            # ---------------------------------------------------

            self.scaler.scale(
                loss
            ).backward()

            # ---------------------------------------------------
            # OPTIMIZER STEP
            # ---------------------------------------------------

            if (
                (batch_idx + 1)
                %
                self.gradient_accumulation_steps
                == 0
            ):

                self.scaler.unscale_(
                    self.optimizer
                )

                torch.nn.utils.clip_grad_norm_(

                    self.model.parameters(),

                    self.max_grad_norm
                )

                self.scaler.step(
                    self.optimizer
                )

                self.scaler.update()

                self.optimizer.zero_grad(
                    set_to_none=True
                )

            # ---------------------------------------------------
            # LOSS REDUCTION
            # ---------------------------------------------------

            reduced_loss = (
                self.metric_reducer.reduce_mean(
                    loss.detach()
                )
            )

            epoch_loss += (
                reduced_loss.item()
                *
                self.gradient_accumulation_steps
            )

            self.global_step += 1

            # ---------------------------------------------------
            # LOGGING
            # ---------------------------------------------------

            if (
                batch_idx %
                self.log_interval
                == 0
            ):

                self.rank_zero_log(
                    f"Epoch={self.current_epoch} | "
                    f"Batch={batch_idx}/{total_batches} | "
                    f"Loss={reduced_loss.item():.6f}"
                )

        average_loss = (
            epoch_loss / total_batches
        )

        self.rank_zero_log(
            f"Epoch {self.current_epoch} completed | "
            f"AverageLoss={average_loss:.6f}"
        )

        return average_loss

    # ============================================================
    # DISTRIBUTED VALIDATION
    # ============================================================

    @torch.no_grad()
    def validate(self):

        self.state_manager.transition(
            TrainingState.VALIDATING
        )

        self.model.eval()

        validation_loss = 0.0

        total_batches = len(
            self.val_loader
        )

        self.rank_zero_log(
            "Distributed validation started."
        )

        for batch in self.val_loader:

            inputs, targets = batch

            inputs = inputs.to(
                self.device,
                non_blocking=True
            )

            targets = targets.to(
                self.device,
                non_blocking=True
            )

            with autocast(
                enabled=self.use_amp
            ):

                outputs = self.model(inputs)

                loss = self.criterion(
                    outputs,
                    targets
                )

            reduced_loss = (
                self.metric_reducer.reduce_mean(
                    loss.detach()
                )
            )

            validation_loss += (
                reduced_loss.item()
            )

        average_validation_loss = (
            validation_loss / total_batches
        )

        self.rank_zero_log(
            f"Validation Loss="
            f"{average_validation_loss:.6f}"
        )

        self.state_manager.transition(
            TrainingState.TRAINING
        )

        return average_validation_loss

    # ============================================================
    # DISTRIBUTED CLEANUP
    # ============================================================

    def cleanup(self):
        """
        Safely cleanup distributed runtime.
        """

        try:

            self.rank_zero_log(
                "Cleaning distributed runtime."
            )

            self.metric_reducer.barrier()

            self.process_group_manager.destroy()

            self.device_manager.cleanup_memory()

            self.rank_zero_log(
                "Distributed cleanup completed."
            )

        except Exception as error:

            self.logger.error(
                f"Distributed cleanup failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

    # ============================================================
    # DISTRIBUTED SUMMARY
    # ============================================================

    def export_distributed_summary(self):

        return {

            "backend": self.backend,

            "rank": self.rank,

            "local_rank": self.local_rank,

            "world_size": self.world_size,

            "device": str(self.device),

            "mixed_precision":
                self.use_amp,

            "distributed_initialized":
                dist.is_initialized(),

            "cuda_available":
                torch.cuda.is_available(),
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"DistributedTrainer("
            f"backend={self.backend}, "
            f"rank={self.rank}, "
            f"world_size={self.world_size})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    print(
        "\nDistributedTrainer module loaded successfully.\n"
    )
