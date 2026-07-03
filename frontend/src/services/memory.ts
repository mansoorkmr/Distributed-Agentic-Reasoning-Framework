import api from "../api/client";

export async function getMemory() {

    const response = await api.get(
        "/memory",
    );

    return response.data;
}