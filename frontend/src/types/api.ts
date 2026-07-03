export interface ChatRequest {
    prompt: string;
    temperature?: number;
    max_tokens?: number;
}

export interface ChatResponse {
    success: boolean;
    message: string;
    response: string;
    agent: string;
}

export interface ExecuteRequest {
    agent: string;
    inputs: Record<string, unknown>;
}

export interface ExecuteResponse {
    success: boolean;
    message: string;
    agent: string;
    output: unknown;
}

export interface AgentsResponse {
    success: boolean;
    message: string;
    agents: string[];
}

export interface MemoryResponse {
    success: boolean;
    message: string;
    memory: Record<string, unknown>;
}