import api from "../api/client";

export async function getTools() {

    const response = await api.get(
        "/tools",
    );

    return response.data;
}