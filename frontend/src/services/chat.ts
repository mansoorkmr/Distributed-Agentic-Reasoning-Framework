import api from "../api/client";
import type {
    ChatRequest,
    ChatResponse,
} from "../types/api";

export async function chat(
    request: ChatRequest,
): Promise<ChatResponse> {

    const response = await api.post(
        "/chat",
        request,
    );

    return response.data;
}