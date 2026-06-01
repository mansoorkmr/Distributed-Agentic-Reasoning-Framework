# Distributed Multi-Agent AI System with LLM Training Pipeline

## Abstract
This project presents a **production-grade, distributed multi-agent AI system** built on top of a **large language model (LLM) training pipeline**. The system integrates multi-domain datasets (reasoning, retrieval, dialogue, and language modeling) into a unified training architecture designed for **stability, reproducibility, and scalability on HPC environments**.

The implementation addresses critical real-world issues in LLM training such as:
- Gradient instability (NaN / overflow)
- Dataset imbalance
- Non-deterministic model loading
- HPC execution failures
- Memory fragmentation in GPU training

The result is a **robust, reproducible, and deployment-ready AI system**.

---

## 1. Problem Statement

Modern AI systems suffer from fragmentation across:
- reasoning models
- retrieval systems
- dialogue agents
- distributed execution

Additionally, training pipelines frequently fail due to:
- unstable precision (FP16 failures)
- dataset dominance bias
- environment inconsistency
- unreliable model loading in offline HPC environments

This project solves these issues by designing a **unified, deterministic training and execution system**.

---

## 2. System Architecture

### 2.1 High-Level Design

---
User Input
↓
Agent Manager (multi-agent orchestration)
↓
Planner → Task Decomposition
↓
LLM Engine (trained model)
↓
Aggregator → Final Response

### 2.2 Core Modules

| Module | Responsibility |
|------|---------------|
| `agents/` | Domain-specific agents (finance, health, task) |
| `core/` | Orchestrator, planner, aggregator |
| `llm/` | LLM inference engine |
| `scripts/training/` | Training pipeline |
| `hpc/` | SLURM job execution |
| `logs/` | Training outputs and metrics |
| `checkpoints/` | Model artifacts |

---

## 3. Key Features

### 3.1 Deterministic Model Loading
- Offline HuggingFace loading via fixed snapshot path
- Eliminates network dependency and runtime failure

### 3.2 Multi-Domain Training
Datasets include:
- Reasoning → GSM8K
- Retrieval → MS MARCO, Natural Questions
- Dialogue → MultiWOZ
- Language Modeling → WikiText, C4

### 3.3 Dataset Balancing
- Interleaving strategy prevents dataset dominance
- Ensures generalization across domains

### 3.4 Training Stability
- FP32 training (V100-safe)
- Gradient clipping
- Label masking (ignore padding tokens)
- Eliminates NaN gradients

### 3.5 HPC Execution
- SLURM-based job execution
- GPU-aware scheduling
- Offline cache usage

### 3.6 Observability
- Training logs
- GPU memory tracking
- Loss and gradient monitoring

---

## 4. Project Structure
Distributed_Multi_Agent_AI_System/
│
├── agents/ # Multi-agent implementations
├── core/ # Orchestration and planning
├── llm/ # Model interface
├── scripts/training/ # Training pipeline
├── hpc/job_scripts/ # SLURM scripts
├── logs/ # Training logs
├── checkpoints/ # Trained model
├── config/ # Configuration
├── README.md # Documentation

---

## 5. Installation
