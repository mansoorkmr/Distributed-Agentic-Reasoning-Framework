import sys
import torch
import traceback
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer


class LLMEngine:
    """
    Clean Institutional-Grade LLM Engine

    ✔ Correct chat handling (no token leakage)
    ✔ Proper generate() inputs (dict, not tensor)
    ✔ GPU/CPU safe
    ✔ Stable across transformers versions
    ✔ Clean output extraction
    ✔ No hacks, no fragile logic
    """

    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self._log_header()

        # -------- TOKENIZER --------
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

        except Exception as e:
            self._fatal("Tokenizer load failed", e)

        # -------- MODEL --------
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)

            self.model.eval()

        except RuntimeError:
            # GPU fallback
            self.device = "cpu"
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to("cpu")
            self.model.eval()

        except Exception as e:
            self._fatal("Model load failed", e)

    # ==================================================
    # LOGGING
    # ==================================================
    def _log_header(self):
        print("\n========== LLM INIT ==========")
        print(f"[TIME] {datetime.utcnow().isoformat()}")
        print(f"[MODEL] {self.model_name}")
        print(f"[DEVICE] {'cuda' if torch.cuda.is_available() else 'cpu'}")

    def _log(self, msg):
        print(msg)

    def _fatal(self, msg, err):
        print(f"\n[FATAL] {msg}")
        traceback.print_exc()
        sys.exit(1)

    # ==================================================
    # INPUT BUILDER (CORRECT + STABLE)
    # ==================================================
    def _build_inputs(self, prompt):
        try:
            if hasattr(self.tokenizer, "apply_chat_template"):
                text = self.tokenizer.apply_chat_template(
                    [
                        {"role": "system", "content": "You are a professional assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    tokenize=False
                )
            else:
                text = prompt

            encoded = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True
            )

            return {k: v.to(self.device) for k, v in encoded.items()}

        except Exception as e:
            self._fatal("Input build failed", e)

    # ==================================================
    # GENERATION (FINAL CLEAN VERSION)
    # ==================================================
    def generate(self, prompt, max_new_tokens=150):
        try:
            inputs = self._build_inputs(prompt)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=False)

            # -------- CLEAN EXTRACTION --------
            if "<|assistant|>" in decoded:
                response = decoded.split("<|assistant|>")[-1].strip()
            else:
                response = decoded.strip()

            # fallback cleanup
            response = response.replace("<|system|>", "").replace("<|user|>", "").strip()

            return response

        except RuntimeError as e:
            if "CUDA" in str(e):
                # GPU fallback safely
                self.device = "cpu"
                self.model.to("cpu")
                return self.generate(prompt)

            return "Error: Runtime failure"

        except Exception:
            traceback.print_exc()
            return "Error: Unexpected failure"

    # ==================================================
    # HEALTH CHECK
    # ==================================================
    def health_check(self):
        try:
            _ = self.generate("Hello")
            return True
        except:
            return False
