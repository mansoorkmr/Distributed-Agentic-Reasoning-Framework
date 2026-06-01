import os
import json

class ResultAggregator:
    def collect(self):
        results = []
        path = "logs/results"

        for file in os.listdir(path):
            with open(os.path.join(path, file)) as f:
                results.append(json.load(f))

        return results
