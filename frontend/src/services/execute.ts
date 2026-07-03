import api from "../api/client";
import type {
    ExecuteRequest,
    ExecuteResponse,
} from "../types/api";

export async function execute(
    request: ExecuteRequest,
): Promise<ExecuteResponse> {

    const response = await api.post(
        "/execute",
        request,
    );

    return response.data;
}