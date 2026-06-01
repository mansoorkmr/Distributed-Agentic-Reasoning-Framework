# LLM Setup (HPC - Local GPU)

## Objective
Integrate a local Large Language Model (LLM) running on GPU nodes for agent reasoning.

## Approach
- Use HuggingFace Transformers
- Run inference on GPU via Slurm jobs
- Integrate LLM into agent execution pipeline

## Model Choice
We use a lightweight but powerful model:

- Mistral-7B-Instruct (if available)
OR
- TinyLlama / Distil models (fallback)
## Model Upgrade

Upgraded from distilgpt2 to TinyLlama (instruction-tuned).

## Improvements
- Better response quality
- GPU-compatible
- Controlled generation

## GPU Execution
Model successfully runs on CUDA-enabled nodes via SLURM.
## Execution Flow
Agent → HPC GPU Job → Load Model → Generate Response → Save Output
