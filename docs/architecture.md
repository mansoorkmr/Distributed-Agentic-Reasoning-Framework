# System Architecture

## High-Level Architecture

User Interface → API Layer → Orchestrator → HPC Cluster → Agents → Result Aggregation

## Components

1. API Layer (FastAPI)
2. Orchestrator
3. Agent Manager
4. HPC Job Scheduler
5. Agent Workers
6. Memory Layer

## Execution Flow

1. User sends request
2. Orchestrator decomposes tasks
3. Jobs submitted to HPC
4. Agents execute in parallel
5. Results aggregated
