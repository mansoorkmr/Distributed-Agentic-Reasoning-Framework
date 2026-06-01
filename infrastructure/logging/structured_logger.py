"""
Distributed Agentic Reasoning Framework (DARF)
Institutional-Grade Structured Logging Infrastructure

Author:
    DARF Infrastructure Division

Purpose:
    Centralized, distributed-safe, fault-tolerant logging
    infrastructure for:

        - distributed training
        - orchestration
        - inference
        - evaluation
        - HPC execution
        - recovery systems
        - experiment lineage

Core Features:
    - structured logging
    - rotating file handlers
    - distributed-safe singleton design
    - console + file synchronization
    - rich traceback support
    - thread-safe architecture
    - future extensibility
    - institutional reproducibility

Design Principles:
    - deterministic
    - scalable
    - production-grade
    - HPC-compatible
    - distributed-safe
    - fault-tolerant
"""

import logging
import os
import traceback

from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock

from rich.console import Console
from rich.logging import RichHandler


class StructuredLogger:
    """
    Institutional-grade structured logging system.

    Supports:
        - distributed execution
        - HPC environments
        - multi-agent orchestration
        - training lifecycle logging
        - centralized observability
    """

    _instances = {}

    _instance_lock = Lock()

    VALID_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # ============================================================
    # SINGLETON CONSTRUCTION
    # ============================================================

    def __new__(cls, name="DARF", *args, **kwargs):

        with cls._instance_lock:

            if name not in cls._instances:

                instance = super().__new__(cls)

                cls._instances[name] = instance

            return cls._instances[name]

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        name="DARF",
        log_dir="logs/system",
        level="INFO",
        max_bytes=50 * 1024 * 1024,
        backup_count=10,
        enable_console=True,
        enable_file=True,
    ):

        # --------------------------------------------------------
        # Prevent duplicate initialization
        # --------------------------------------------------------

        if hasattr(self, "_initialized"):

            return

        self._initialized = True

        self.name = name

        self.log_dir = Path(log_dir)

        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.console = Console()

        self.logger = logging.getLogger(name)

        self.logger.setLevel(self.VALID_LEVELS.get(level.upper(), logging.INFO))

        self.logger.propagate = False

        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        self.log_file = self.log_dir / f"{name}_{self.timestamp}.log"

        # --------------------------------------------------------
        # Formatter
        # --------------------------------------------------------

        formatter = logging.Formatter(
            fmt=(
                "[%(asctime)s] "
                "[%(levelname)s] "
                "[%(name)s] "
                "[%(filename)s:%(lineno)d] "
                "%(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # --------------------------------------------------------
        # Prevent duplicate handlers
        # --------------------------------------------------------

        if not self.logger.handlers:

            # ----------------------------------------------------
            # FILE HANDLER
            # ----------------------------------------------------

            if enable_file:

                file_handler = RotatingFileHandler(
                    filename=self.log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8",
                )

                file_handler.setLevel(
                    self.VALID_LEVELS.get(level.upper(), logging.INFO)
                )

                file_handler.setFormatter(formatter)

                self.logger.addHandler(file_handler)

            # ----------------------------------------------------
            # CONSOLE HANDLER
            # ----------------------------------------------------

            if enable_console:

                console_handler = RichHandler(
                    rich_tracebacks=True,
                    show_path=True,
                    markup=True,
                )

                console_handler.setLevel(
                    self.VALID_LEVELS.get(level.upper(), logging.INFO)
                )

                console_handler.setFormatter(formatter)

                self.logger.addHandler(console_handler)

    # ============================================================
    # INTERNAL LOGGING CORE
    # ============================================================

    def _log(self, level, message):

        if not isinstance(message, str):

            message = str(message)

        self.logger.log(level, message)

    # ============================================================
    # PUBLIC LOGGING METHODS
    # ============================================================

    def debug(self, message):

        self._log(logging.DEBUG, message)

    def info(self, message):

        self._log(logging.INFO, message)

    def warning(self, message):

        self._log(logging.WARNING, message)

    def error(self, message):

        self._log(logging.ERROR, message)

    def critical(self, message):

        self._log(logging.CRITICAL, message)

    # ============================================================
    # EXCEPTION LOGGING
    # ============================================================

    def exception(self, message):
        """
        Log full traceback safely.
        """

        formatted_traceback = traceback.format_exc()

        self.logger.error(f"{message}\n{formatted_traceback}")

    # ============================================================
    # SYSTEM EVENT HELPERS
    # ============================================================

    def log_system_event(
        self,
        component,
        state,
        details=None,
    ):

        message = f"[SYSTEM_EVENT] " f"Component={component} | " f"State={state}"

        if details:

            message += f" | Details={details}"

        self.info(message)

    # ============================================================
    # TRAINING EVENT HELPERS
    # ============================================================

    def log_training_event(
        self,
        epoch,
        loss,
        learning_rate=None,
    ):

        message = f"[TRAINING] " f"Epoch={epoch} | " f"Loss={loss:.6f}"

        if learning_rate is not None:

            message += f" | LR={learning_rate}"

        self.info(message)

    # ============================================================
    # CHECKPOINT EVENT HELPERS
    # ============================================================

    def log_checkpoint_event(
        self,
        checkpoint_path,
    ):

        self.info(f"[CHECKPOINT] " f"Saved at: {checkpoint_path}")

    # ============================================================
    # RECOVERY EVENT HELPERS
    # ============================================================

    def log_recovery_event(
        self,
        recovery_type,
        status,
    ):

        self.warning(f"[RECOVERY] " f"Type={recovery_type} | " f"Status={status}")

    # ============================================================
    # CLEAN SHUTDOWN
    # ============================================================

    def shutdown(self):
        """
        Gracefully close all handlers.
        """

        handlers = self.logger.handlers[:]

        for handler in handlers:

            handler.close()

            self.logger.removeHandler(handler)

    # ============================================================
    # STRING REPRESENTATION
    # ============================================================

    def __str__(self):

        return f"StructuredLogger(" f"name={self.name})"


# ================================================================
# GLOBAL LOGGER FACTORY
# ================================================================


def get_logger(
    name="DARF",
    log_dir="logs/system",
    level="INFO",
):
    """
    Global structured logger factory.
    """

    return StructuredLogger(
        name=name,
        log_dir=log_dir,
        level=level,
    )


# ================================================================
# STANDALONE VALIDATION
# ================================================================

if __name__ == "__main__":

    logger = get_logger(
        name="DARF_TEST",
        level="DEBUG",
    )

    logger.info("Structured logger initialized.")

    logger.debug("Debug logging active.")

    logger.warning("Warning logging active.")

    logger.error("Error logging active.")

    logger.log_system_event(
        component="Orchestrator",
        state="INITIALIZED",
    )

    logger.log_training_event(
        epoch=1,
        loss=0.2345,
        learning_rate=1e-4,
    )

    try:

        _ = 1 / 0

    except Exception:

        logger.exception("Exception captured successfully.")

    logger.shutdown()
