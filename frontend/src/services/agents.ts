import api from "../api/client";

export async function getAgents() {

    const response = await api.get(
        "/agents",
    );

    return response.data;
}