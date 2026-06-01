import json
import os
from datetime import datetime

from llm.llm_engine import LLMEngine
from memory.manager.memory_manager import MemoryManager


# ==================================================
# CONFIG
# ==================================================
RESULT_PATH = "logs/results/finance.json"


# ==================================================
# AGENT CLASS (CLEAN + MODULAR)
# ==================================================
class FinanceAgent:
    """
    Institutional-Grade Finance Agent

    Responsibilities:
    - Query processing
    - Memory retrieval (RAG)
    - LLM invocation
    - Memory storage
    - Result persistence
    """

    def __init__(self):
        print("\n========================================")
        print("        FINANCE AGENT INITIALIZED")
        print("========================================")

        self.llm = LLMEngine()
        self.memory = MemoryManager()

    # ==================================================
    # PROMPT TEMPLATE
    # ==================================================
    def _build_prompt(self, query):
        return f"""
You are a professional financial advisor.

Provide structured, practical advice on:

1. Saving money
2. Budgeting strategies
3. Investment planning

Ensure:
- clear explanation
- actionable steps
- real-world applicability

User Query:
{query}
"""

    # ==================================================
    # MAIN EXECUTION
    # ==================================================
    def run(self, query: str):
        try:
            print("[INFO] Starting agent execution...")

            # -------------------------------
            # STEP 1: BUILD BASE PROMPT
            # -------------------------------
            base_prompt = self._build_prompt(query)

            # -------------------------------
            # STEP 2: AUGMENT WITH MEMORY (RAG)
            # -------------------------------
            augmented_prompt = self.memory.augment_prompt(base_prompt)

            # -------------------------------
            # STEP 3: LLM GENERATION
            # -------------------------------
            response = self.llm.generate(augmented_prompt)

            # -------------------------------
            # STEP 4: STORE MEMORY
            # -------------------------------
            self.memory.store(query, response)

            # -------------------------------
            # STEP 5: SAVE RESULT
            # -------------------------------
            result = {
                "agent": "finance",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "output": response
            }

            self._save_result(result)

            print("[INFO] Agent execution completed")
            return result

        except Exception as e:
            print("[ERROR] Agent execution failed:", str(e))

            result = {
                "agent": "finance",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "output": str(e)
            }

            self._save_result(result)
            return result

    # ==================================================
    # SAVE RESULT (SAFE)
    # ==================================================
    def _save_result(self, data):
        try:
            os.makedirs(os.path.dirname(RESULT_PATH), exist_ok=True)

            with open(RESULT_PATH, "w") as f:
                json.dump(data, f, indent=4)

            print(f"[INFO] Results saved to {RESULT_PATH}")

        except Exception as e:
            print("[ERROR] Failed to save results:", str(e))


# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
def main():
    query = """
Give me financial advice for saving money and investing wisely.
"""

    agent = FinanceAgent()
    agent.run(query)


if __name__ == "__main__":
    main()
