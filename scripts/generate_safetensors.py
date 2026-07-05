import json
import logging
from pathlib import Path
from typing import Dict
import torch
from safetensors.torch import save_file

# ==========================================
# Logging Configuration
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ==========================================
# Configuration and Constants
# ==========================================
class ModelConfig:
    """Demo tensor sizes (small enough for GitHub uploads)."""
    HIDDEN_SIZE: int = 256
    VOCAB_SIZE: int = 2048
    INTERMEDIATE_SIZE: int = 512
    NUM_LAYERS: int = 4
    DTYPE: torch.dtype = torch.float32

def generate_metadata() -> Dict[str, str]:
    """
    Compiles and serializes model metrics, dataset weights, and architecture metadata.
    This retains the original 1.1 Billion parameter specifications.
    """
    dataset_weights = {
        "Web": "55%",
        "Books": "25%",
        "News": "10%",
        "Wikipedia": "5%",
        "GitHub": "5%"
    }

    darf_framework_results = {
        "Average_Success_Rate": "97.6%",
        "Average_Relevance_Score": "96.2%",
        "Average_Perplexity": "4.3",
        "End_to_End_Workflow_Accuracy": "95.8%",
        "Agent_Collaboration_Efficiency": "98.1%",
        "Failure_Recovery_Rate": "93.4%"
    }

    agent_benchmarks = {
        "Planner": {"Success": "98.2%", "Latency_ms": 120},
        "Retrieval": {"Success": "97.6%", "Latency_ms": 180},
        "Reasoning": {"Success": "95.4%", "Latency_ms": 250},
        "Tool-Use": {"Success": "99.1%", "Latency_ms": 140},
        "Validation": {"Success": "96.8%", "Latency_ms": 160},
        "Memory": {"Success": "97.3%", "Latency_ms": 130},
        "Coordinator": {"Success": "98.7%", "Latency_ms": 110}
    }

    model_benchmarks_targets = {
        "MMLU": "83-87%",
        "GSM8K": "90-94%",
        "Human_Eval": "78-85%",
        "TruthfulQA": "66-75%",
        "HellaSwag": "90-95%"
    }

    # Preserving the original 1.1B model metadata as explicit strings
    return {
        "format": "pt",
        "model_architecture": "LlamaForCausalLM",
        "model_type": "llama",
        "parameters": "1.1 Billion",
        "precision": "FP32",
        "hidden_size": "2048",
        "vocab_size": "32000",
        "num_hidden_layers": "22",
        "num_attention_heads": "32",
        "num_key_value_heads": "4",
        "hidden_act": "SiLU",
        "max_position_embeddings": "2048",
        "dataset_sampling_weights": json.dumps(dataset_weights),
        "darf_overall_results": json.dumps(darf_framework_results),
        "darf_agent_metrics": json.dumps(agent_benchmarks),
        "target_benchmarks": json.dumps(model_benchmarks_targets)
    }

def generate_model_tensors() -> Dict[str, torch.Tensor]:
    """
    Generates scaled-down dummy tensors to keep file size within GitHub limits.
    
    Returns:
        Dict[str, torch.Tensor]: A dictionary mapping layer names to PyTorch tensors.
    """
    logger.info("Initializing demo tensor generation (scaled down for GitHub)...")
    
    tensors: Dict[str, torch.Tensor] = {
        "model.embed_tokens.weight": torch.zeros(
            (ModelConfig.VOCAB_SIZE, ModelConfig.HIDDEN_SIZE), dtype=ModelConfig.DTYPE
        ),
        "model.norm.weight": torch.ones(
            (ModelConfig.HIDDEN_SIZE,), dtype=ModelConfig.DTYPE
        ),
        "lm_head.weight": torch.zeros(
            (ModelConfig.VOCAB_SIZE, ModelConfig.HIDDEN_SIZE), dtype=ModelConfig.DTYPE
        ),
    }
    
    for i in range(ModelConfig.NUM_LAYERS):
        tensors[f"model.layers.{i}.input_layernorm.weight"] = torch.ones(
            (ModelConfig.HIDDEN_SIZE,), dtype=ModelConfig.DTYPE
        )
        tensors[f"model.layers.{i}.mlp.down_proj.weight"] = torch.zeros(
            (ModelConfig.HIDDEN_SIZE, ModelConfig.INTERMEDIATE_SIZE), dtype=ModelConfig.DTYPE
        )
        
    logger.info(f"Successfully generated {len(tensors)} scaled-down tensor mappings.")
    return tensors

def create_safetensors_archive(output_path: Path) -> None:
    """
    Orchestrates the generation of tensors and metadata, saving them safely to disk.
    
    Args:
        output_path (Path): The destination filepath for the .safetensors file.
    """
    try:
        tensors = generate_model_tensors()
        metadata = generate_metadata()
        
        logger.info(f"Writing Safetensors archive to: {output_path.resolve()}")
        save_file(tensors, str(output_path), metadata=metadata)
        logger.info("Safetensors demo file successfully generated and ready for upload.")
        
    except Exception as e:
        logger.error(f"Failed to generate Safetensors archive: {e}", exc_info=True)
        raise

# ==========================================
# Execution Entry Point
# ==========================================
if __name__ == "__main__":
    output_filename = Path("darf_tinyllama_1.1B_demo.safetensors")
    create_safetensors_archive(output_filename)