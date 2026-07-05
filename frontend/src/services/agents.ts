import api from "../api/client";

export interface AgentInfo {

    id: string;

    name: string;

    description: string;

    version: string;

    status: string;

    capabilities: string[];

}

export interface AgentsResponse {

    success: boolean;

    message: string;

    count: number;

    agents: AgentInfo[];

}

export async function getAgents(): Promise<AgentsResponse> {

    const response = await api.get("/agents");

    return response.data;

}