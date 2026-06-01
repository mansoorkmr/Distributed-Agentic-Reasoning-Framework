#!/bin/bash
#SBATCH --job-name=agent_llm

#SBATCH --output=logs/output_%j.txt
#SBATCH --error=logs/error_%j.txt

#SBATCH --partition=gpu
#SBATCH --gres=gpu:1

#SBATCH --cpus-per-task=6
#SBATCH --mem=64G
#SBATCH --time=48:00:00

# =========================================================
# 🔒 1. FAIL FAST (NO SILENT FAILURES)
# =========================================================
set -e
set -o pipefail

echo "========================================"
echo "         HPC JOB STARTED"
echo "========================================"
echo "[INFO] Job ID: $SLURM_JOB_ID"
echo "[INFO] Node: $(hostname)"
echo "[INFO] Start Time: $(date)"

# =========================================================
# 🔧 2. ENVIRONMENT SETUP
# =========================================================
echo "[INFO] Activating environment..."

source ~/.bashrc
source venv/bin/activate

echo "[ENV] Python path: $(which python)"

# =========================================================
# 🚀 3. CRITICAL ENV VARIABLES (FINAL — NO COMPROMISE)
# =========================================================

# 🔥 USE LUSTRE (PERSISTENT STORAGE — CORRECT FIX)
export HF_HOME=/lustre/mansoor.wani/hf_cache
export TRANSFORMERS_OFFLINE=1

# 🔥 REMOVE OLD/DEPRECATED CACHE VAR
unset TRANSFORMERS_CACHE

# 🔥 CUDA MEMORY FRAGMENTATION FIX
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# 🔥 TOKENIZER SAFETY
export TOKENIZERS_PARALLELISM=false

# 🔥 NCCL STABILITY (CLUSTER SAFE)
export NCCL_DEBUG=warn
export NCCL_IB_DISABLE=1
export NCCL_P2P_DISABLE=1

echo "[ENV] HF_HOME: $HF_HOME"

# =========================================================
# 📂 4. ENSURE DIRECTORIES
# =========================================================
mkdir -p logs
mkdir -p checkpoints/llm

# =========================================================
# 🧪 5. GPU VALIDATION (MANDATORY)
# =========================================================
echo "[CHECK] Validating GPU..."

python - <<EOF
import torch

print("CUDA available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("❌ CUDA NOT AVAILABLE")

print("GPU:", torch.cuda.get_device_name(0))
print("Capability:", torch.cuda.get_device_capability(0))
EOF

# =========================================================
# 🧹 6. CLEAR CUDA CACHE
# =========================================================
echo "[INFO] Clearing CUDA cache..."

python - <<EOF
import torch
torch.cuda.empty_cache()
EOF

# =========================================================
# 📦 7. VERIFY MODEL EXISTS (CRITICAL — NO GUESSING)
# =========================================================
MODEL_BASE="/lustre/mansoor.wani/hf_cache/models--TinyLlama--TinyLlama-1.1B-Chat-v1.0/snapshots"

if [ ! -d "$MODEL_BASE" ]; then
    echo "[ERROR] Model snapshot directory NOT FOUND at $MODEL_BASE"
    exit 1
fi

SNAPSHOT=$(ls $MODEL_BASE | head -n 1)

if [ -z "$SNAPSHOT" ]; then
    echo "[ERROR] No snapshot found inside $MODEL_BASE"
    exit 1
fi

MODEL_PATH="$MODEL_BASE/$SNAPSHOT"

echo "[CHECK] Using model snapshot:"
echo "$MODEL_PATH"

# =========================================================
# 🧪 8. VERIFY MODEL LOAD (FAIL EARLY)
# =========================================================
echo "[CHECK] Verifying model load..."

python - <<EOF
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = "$MODEL_PATH"

tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

print("MODEL LOAD VERIFIED")
EOF

# =========================================================
# 🚀 9. RUN TRAINING SCRIPT
# =========================================================
SCRIPT=$1

if [ -z "$SCRIPT" ]; then
    echo "[ERROR] No training script provided"
    exit 1
fi

echo "[INFO] Running script: $SCRIPT"

python $SCRIPT

EXIT_CODE=$?

# =========================================================
# 🧾 10. FINAL STATUS
# =========================================================
if [ $EXIT_CODE -eq 0 ]; then
    echo "[SUCCESS] Training completed successfully"
else
    echo "[ERROR] Script failed with exit code: $EXIT_CODE"
fi

echo "[INFO] End Time: $(date)"

echo "========================================"
echo "         HPC JOB COMPLETED"
echo "========================================"

exit $EXIT_CODE
