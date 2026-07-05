import { useEffect, useState } from "react";

import {
    getAgents,
    type AgentInfo,
} from "../services/agents";

export function useAgents() {

    const [agents, setAgents] = useState<AgentInfo[]>([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState<string | null>(null);

    async function loadAgents() {

        setLoading(true);

        setError(null);

        try {

            const response = await getAgents();

            setAgents(response.agents);

        }

        catch (err) {

            console.error(err);

            setError("Unable to load agents.");

        }

        finally {

            setLoading(false);

        }

    }

    useEffect(() => {

        loadAgents();

    }, []);

    return {

        agents,

        loading,

        error,

        refresh: loadAgents,

    };

}