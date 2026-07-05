import api from "../api/client";

export interface MemoryMetrics {

    variables: number;

    outputs: number;

}

export interface MemoryContext {

    request_id: string | null;

    session_id: string | null;

    execution_id: string | null;

    current_agent: string | null;

    variables: Record<string, unknown>;

    outputs: Record<string, unknown>;

    metadata: Record<string, unknown>;

    version: string;

}

export interface MemoryResponse {

    success: boolean;

    message: string;

    status: string;

    vector_store: string;

    embedding_model: string;

    top_k: number;

    memory_size: number;

    metrics: MemoryMetrics;

    context: MemoryContext;

}

export async function getMemory(): Promise<MemoryResponse> {

    const response = await api.get("/memory");

    return response.data;

}