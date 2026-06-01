from fastapi import FastAPI
from core.orchestrator import Orchestrator

app = FastAPI()

orchestrator = Orchestrator()

@app.post("/query")
def query(q: str):
    return orchestrator.handle_request(q)
