import os

class AgentManager:
    def __init__(self):
        self.agent_map = {
            "finance": "agents/finance_agent.py",
            "health": "agents/health_agent.py",
            "task": "agents/task_agent.py"
        }

    def get_agent_script(self, task):
        return self.agent_map.get(task)
