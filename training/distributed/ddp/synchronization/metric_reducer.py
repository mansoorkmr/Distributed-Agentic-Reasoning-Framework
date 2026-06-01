"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Distributed Metric Reduction Infrastructure

Author:
    DARF Distributed Systems Division

Purpose:
    Centralized distributed metric synchronization and reduction
    engine for:

        - Distributed Data Parallel (DDP)
        - multi-GPU evaluation
        - synchronized validation
        - distributed inference
        - large-scale benchmarking
        - HPC metric aggregation
        - institutional reproducibility

Core Responsibilities:
    - distributed metric synchronization
    - cross-rank aggregation
    - tensor reduction
    - metric consistency validation
    - fault-tolerant synchronization
    - distributed-safe averaging
    - statistical aggregation
    - scalable metric computation

Design Principles:
    - deterministic
    - numerically stable
    - distributed-safe
    - fault-tolerant
    - HPC-compatible
    - production-grade
    - future extensible

Supported Reductions:
    - SUM
    - MEAN
    - MAX
    - MIN
    - GATHER
    - CONCATENATION
"""

import traceback

import torch
import torch.distributed as dist

from infrastructure.logging.structured_logger import (
    get_logger
)


class MetricReducer:
    """
    Institutional-grade distributed metric reduction engine.

    Handles:
        - synchronized distributed metrics
        - cross-rank tensor aggregation
        - fault-tolerant reduction
        - distributed-safe averaging
        - scalable evaluation synchronization
    """

    def __init__(
        self,
        validate_distributed_state=True
    ):

        self.validate_distributed_state = (
            validate_distributed_state
        )

        self.logger = get_logger(
            name="MetricReducer",
            log_dir="logs/evaluation"
        )

    # ============================================================
    # DISTRIBUTED VALIDATION
    # ============================================================

    def _validate_runtime(self):
        """
        Validate distributed runtime safely.
        """

        if not dist.is_available():

            raise RuntimeError(
                "torch.distributed unavailable."
            )

        if not dist.is_initialized():

            raise RuntimeError(
                "Distributed process group "
                "not initialized."
            )

    # ============================================================
    # DEVICE NORMALIZATION
    # ============================================================

    def _normalize_tensor(
        self,
        tensor
    ):
        """
        Ensure tensor compatibility.
        """

        if not isinstance(
            tensor,
            torch.Tensor
        ):

            tensor = torch.tensor(
                tensor,
                dtype=torch.float32
            )

        if torch.cuda.is_available():

            tensor = tensor.cuda()

        return tensor

    # ============================================================
    # SUM REDUCTION
    # ============================================================

    def reduce_sum(
        self,
        tensor
    ):
        """
        Distributed SUM reduction.

        Formula:
            x = Σ(x_i)
        """

        if self.validate_distributed_state:

            self._validate_runtime()

        tensor = self._normalize_tensor(
            tensor
        )

        reduced = tensor.clone()

        dist.all_reduce(
            reduced,
            op=dist.ReduceOp.SUM
        )

        return reduced

    # ============================================================
    # MEAN REDUCTION
    # ============================================================

    def reduce_mean(
        self,
        tensor
    ):
        """
        Distributed MEAN reduction.

        Formula:
            x̄ = (1/N) * Σ(x_i)
        """

        if self.validate_distributed_state:

            self._validate_runtime()

        tensor = self._normalize_tensor(
            tensor
        )

        reduced = tensor.clone()

        dist.all_reduce(
            reduced,
            op=dist.ReduceOp.SUM
        )

        reduced /= dist.get_world_size()

        return reduced

    # ============================================================
    # MAX REDUCTION
    # ============================================================

    def reduce_max(
        self,
        tensor
    ):
        """
        Distributed MAX reduction.
        """

        if self.validate_distributed_state:

            self._validate_runtime()

        tensor = self._normalize_tensor(
            tensor
        )

        reduced = tensor.clone()

        dist.all_reduce(
            reduced,
            op=dist.ReduceOp.MAX
        )

        return reduced

    # ============================================================
    # MIN REDUCTION
    # ============================================================

    def reduce_min(
        self,
        tensor
    ):
        """
        Distributed MIN reduction.
        """

        if self.validate_distributed_state:

            self._validate_runtime()

        tensor = self._normalize_tensor(
            tensor
        )

        reduced = tensor.clone()

        dist.all_reduce(
            reduced,
            op=dist.ReduceOp.MIN
        )

        return reduced

    # ============================================================
    # ALL GATHER
    # ============================================================

    def all_gather(
        self,
        tensor
    ):
        """
        Gather tensors from all ranks.
        """

        if self.validate_distributed_state:

            self._validate_runtime()

        tensor = self._normalize_tensor(
            tensor
        )

        gathered = [

            torch.zeros_like(tensor)

            for _ in range(
                dist.get_world_size()
            )
        ]

        dist.all_gather(
            gathered,
            tensor
        )

        return gathered

    # ============================================================
    # CONCATENATION GATHER
    # ============================================================

    def gather_and_concatenate(
        self,
        tensor,
        dim=0
    ):
        """
        Gather tensors and concatenate.
        """

        gathered = self.all_gather(
            tensor
        )

        return torch.cat(
            gathered,
            dim=dim
        )

    # ============================================================
    # DISTRIBUTED SCALAR REDUCTION
    # ============================================================

    def reduce_scalar_mean(
        self,
        scalar
    ):
        """
        Distributed-safe scalar averaging.
        """

        tensor = torch.tensor(
            scalar,
            dtype=torch.float32
        )

        reduced = self.reduce_mean(
            tensor
        )

        return reduced.item()

    # ============================================================
    # DISTRIBUTED METRIC DICTIONARY
    # ============================================================

    def reduce_metric_dict(
        self,
        metrics
    ):
        """
        Reduce dictionary of metrics safely.

        Example:
            {
                "loss": 0.5,
                "accuracy": 0.92
            }
        """

        reduced_metrics = {}

        for key, value in metrics.items():

            reduced_metrics[key] = (
                self.reduce_scalar_mean(value)
            )

        return reduced_metrics

    # ============================================================
    # SYNCHRONIZATION BARRIER
    # ============================================================

    def barrier(self):
        """
        Global distributed synchronization barrier.
        """

        if self.validate_distributed_state:

            self._validate_runtime()

        dist.barrier()

    # ============================================================
    # NUMERICAL STABILITY VALIDATION
    # ============================================================

    def validate_tensor(
        self,
        tensor
    ):
        """
        Validate tensor numerical integrity.
        """

        if torch.isnan(tensor).any():

            raise RuntimeError(
                "NaN detected in distributed tensor."
            )

        if torch.isinf(tensor).any():

            raise RuntimeError(
                "Inf detected in distributed tensor."
            )

    # ============================================================
    # SAFE REDUCTION WRAPPER
    # ============================================================

    def safe_reduce_mean(
        self,
        tensor
    ):
        """
        Fault-tolerant mean reduction wrapper.
        """

        try:

            reduced = self.reduce_mean(
                tensor
            )

            self.validate_tensor(
                reduced
            )

            return reduced

        except Exception as error:

            self.logger.error(
                f"Distributed reduction failed: "
                f"{error}"
            )

            self.logger.error(
                traceback.format_exc()
            )

            raise error

    # ============================================================
    # RANK HELPERS
    # ============================================================

    @staticmethod
    def get_rank():

        if (
            dist.is_available()
            and dist.is_initialized()
        ):

            return dist.get_rank()

        return 0

    @staticmethod
    def get_world_size():

        if (
            dist.is_available()
            and dist.is_initialized()
        ):

            return dist.get_world_size()

        return 1

    @staticmethod
    def is_main_process():

        return (
            MetricReducer.get_rank() == 0
        )

    # ============================================================
    # EXECUTION SUMMARY
    # ============================================================

    def export_runtime_summary(self):

        return {

            "distributed_available":
                dist.is_available(),

            "distributed_initialized":
                (
                    dist.is_initialized()
                    if dist.is_available()
                    else False
                ),

            "rank":
                self.get_rank(),

            "world_size":
                self.get_world_size(),
        }

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return (
            f"MetricReducer("
            f"rank={self.get_rank()}, "
            f"world_size={self.get_world_size()})"
        )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    reducer = MetricReducer(
        validate_distributed_state=False
    )

    tensor = torch.tensor([1.0, 2.0, 3.0])

    print("\nTensor:\n")

    print(tensor)

    print("\nRuntime Summary:\n")

    print(
        reducer.export_runtime_summary()
    )
