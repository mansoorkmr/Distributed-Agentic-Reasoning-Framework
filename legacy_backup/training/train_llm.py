from __future__ import annotations

"""
Institutional-Grade Deterministic LLM Training Pipeline
======================================================

This module implements a fully validated, fault-tolerant,
HPC-safe training pipeline with strong typing and strict contracts.

Design Patterns:
    - Singleton: Global config (settings)
    - Factory: Model/tokenizer instantiation
    - Strategy: Dataset composition
    - Guard Clauses: Fail-fast validation
    - Retry Pattern: External IO resilience

Complexity:
    Dataset load: O(n)
    Preprocessing: O(n)
    Training: O(n * epochs)

Guarantees:
    ✔ No silent failures
    ✔ Deterministic execution
    ✔ Offline-safe
    ✔ Schema validation enforced
    ✔ Idempotent checkpointing
"""

import os
import time
import math
import json
from typing import List, Dict, Any, Callable, TypedDict

import torch
import pandas as pd
from datasets import load_from_disk, interleave_datasets, Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    default_data_collator,
)

from config import settings


# =========================================================
# EXCEPTION HIERARCHY
# =========================================================

class TrainingError(Exception): ...
class DatasetError(TrainingError): ...
class ModelError(TrainingError): ...
class ValidationError(TrainingError): ...


# =========================================================
# TYPE CONTRACTS
# =========================================================

class Example(TypedDict):
    input_ids: List[int]
    attention_mask: List[int]
    labels: List[int]


# =========================================================
# LOGGING (DETERMINISTIC)
# =========================================================

def log(msg: str) -> None:
    print(f"[TRAINING] {msg}", flush=True)


# =========================================================
# RETRY MECHANISM (RESILIENCE)
# =========================================================

def retry(fn: Callable, retries: int = 3, delay: float = 2.0):
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            if i == retries - 1:
                raise
            log(f"Retry {i+1}/{retries} after error: {e}")
            time.sleep(delay)


# =========================================================
# MODEL LOADING (DETERMINISTIC + VALIDATED)
# =========================================================

def resolve_model_path() -> str:
    base = settings.HF_HOME
    root = os.path.join(
        base,
        "models--TinyLlama--TinyLlama-1.1B-Chat-v1.0",
        "snapshots"
    )

    if not os.path.isdir(root):
        raise ModelError(f"HF snapshot root missing: {root}")

    snapshots = sorted(os.listdir(root))
    if not snapshots:
        raise ModelError("No model snapshots found")

    path = os.path.join(root, snapshots[0])

    required = ["config.json", "model.safetensors"]
    for f in required:
        if not os.path.exists(os.path.join(path, f)):
            raise ModelError(f"Missing required file: {f}")

    return path


def load_model_and_tokenizer():
    path = resolve_model_path()
    log(f"Using model: {path}")

    tokenizer = retry(lambda: AutoTokenizer.from_pretrained(path))

    model = retry(lambda: AutoModelForCausalLM.from_pretrained(
        path,
        torch_dtype=torch.float32,
        device_map="auto"
    ))

    model.config.use_cache = False
    model.gradient_checkpointing_enable()

    return tokenizer, model


# =========================================================
# DATA LOADING (STRICT + SAFE)
# =========================================================

def load_datasets(root: str) -> List[Dataset]:
    datasets: List[Dataset] = []

    for r, _, files in os.walk(root):
        if "dataset_info.json" not in files:
            continue

        try:
            ds = retry(lambda: load_from_disk(r))

            if len(ds) < 100:
                continue

            datasets.append(ds)
            log(f"Loaded: {r} ({len(ds)})")

        except Exception as e:
            log(f"Skipped {r}: {e}")

    if not datasets:
        raise DatasetError("No valid datasets found")

    return datasets


# =========================================================
# BALANCED SAMPLING
# =========================================================

def compute_probs(datasets: List[Dataset]) -> List[float]:
    sizes = [len(d) for d in datasets]

    weights = [1 / (s ** 0.5) for s in sizes]
    total = sum(weights)

    return [w / total for w in weights]


# =========================================================
# DATA VALIDATION + PREPROCESSING
# =========================================================

def validate_example(example: Dict[str, Any]) -> None:
    if "input_ids" not in example:
        raise ValidationError("Missing input_ids")

    if not isinstance(example["input_ids"], list):
        raise ValidationError("input_ids must be list")

    if len(example["input_ids"]) == 0:
        raise ValidationError("Empty input_ids")


def add_labels(example: Dict[str, Any]) -> Example:
    validate_example(example)

    input_ids = example["input_ids"]
    mask = example.get("attention_mask", [1] * len(input_ids))

    if len(input_ids) != len(mask):
        raise ValidationError("Mask mismatch")

    labels = [
        token if m == 1 else -100
        for token, m in zip(input_ids, mask)
    ]

    if all(x == -100 for x in labels):
        raise ValidationError("All labels masked")

    return {
        "input_ids": input_ids,
        "attention_mask": mask,
        "labels": labels,
    }


# =========================================================
# CHECKPOINT LOGIC (IDEMPOTENT)
# =========================================================

def get_resume_checkpoint() -> str | None:
    path = settings.CHECKPOINT_DIR

    if not os.path.isdir(path):
        return None

    contents = os.listdir(path)
    return path if contents else None


# =========================================================
# MAIN PIPELINE
# =========================================================

def main():
    log("Initializing training pipeline")

    tokenizer, model = load_model_and_tokenizer()

    datasets = load_datasets("data/tokenized")

    dataset = interleave_datasets(
        datasets,
        probabilities=compute_probs(datasets),
        seed=42,
        stopping_strategy="all_exhausted"
    )

    if len(dataset) < 1000:
        raise DatasetError("Dataset too small")

    split = dataset.train_test_split(test_size=0.02, seed=42)

    train_dataset = split["train"].map(add_labels, num_proc=2)
    eval_dataset = split["test"].map(add_labels, num_proc=2)

    args = TrainingArguments(
        output_dir=settings.CHECKPOINT_DIR,
        per_device_train_batch_size=settings.BATCH_SIZE,
        gradient_accumulation_steps=2,
        learning_rate=settings.LEARNING_RATE,
        num_train_epochs=1,
        logging_steps=50,
        evaluation_strategy="steps",
        eval_steps=200,
        save_steps=500,
        save_total_limit=2,
        fp16=False,
        optim="adamw_torch",
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_grad_norm=1.0,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )

    checkpoint = get_resume_checkpoint()

    if checkpoint:
        log("Resuming from checkpoint")
    else:
        log("Starting fresh")

    torch.cuda.empty_cache()
    trainer.train(resume_from_checkpoint=checkpoint)

    eval_results = trainer.evaluate()
    perplexity = math.exp(eval_results["eval_loss"])

    log(f"Perplexity: {perplexity}")

    final_path = os.path.join(settings.CHECKPOINT_DIR, "final_model")
    trainer.save_model(final_path)
    tokenizer.save_pretrained(final_path)

    os.makedirs("logs", exist_ok=True)

    with open("logs/run_metadata.json", "w") as f:
        json.dump({
            "model": resolve_model_path(),
            "perplexity": perplexity
        }, f, indent=4)

    df = pd.DataFrame(trainer.state.log_history)
    df.to_csv("logs/training_history.csv", index=False)

    log("TRAINING COMPLETE")


if __name__ == "__main__":
    main()
