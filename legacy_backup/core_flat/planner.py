class TaskPlanner:
    def decompose(self, request: str):
        """
        Convert user request into structured tasks
        """
        tasks = []

        if "finance" in request:
            tasks.append("finance")

        if "health" in request:
            tasks.append("health")

        if "task" in request:
            tasks.append("task")

        return tasks
