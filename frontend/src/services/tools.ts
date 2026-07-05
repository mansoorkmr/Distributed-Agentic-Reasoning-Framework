import api from "../api/client";

export interface ToolInfo {

    name: string;

    status: string;

    category: string;

}

export interface ToolResponse {

    success: boolean;

    message: string;

    count: number;

    capabilities: string[];

    tools: ToolInfo[];

}

export async function getTools(): Promise<ToolResponse> {

    const response = await api.get("/tools");

    return response.data;

}