import os
from core.planner import TaskPlanner
from core.agent_manager import AgentManager
from hpc.submit_job import submit_job


class Orchestrator:
    def __init__(self):
        self.planner = TaskPlanner()
        self.agent_manager = AgentManager()

    def handle_request(self, request: str):
        print(f"[Orchestrator] Request: {request}")

        # Step 1: Plan tasks
        tasks = self.planner.decompose(request)

        job_ids = []

        # Step 2: Submit jobs to HPC
        for task in tasks:
            agent_script = self.agent_manager.get_agent_script(task)

            job_id = submit_job(agent_script)
            job_ids.append(job_id)

        return {
            "status": "submitted",
            "jobs": job_ids
        }
