import { useEffect, useState } from "react";

import {
    getTools,
    type ToolResponse,
} from "../services/tools";

export function useTools() {

    const [tools, setTools] = useState<ToolResponse | null>(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState<string | null>(null);

    async function loadTools() {

        setLoading(true);

        setError(null);

        try {

            const response = await getTools();

            setTools(response);

        }

        catch (err) {

            console.error(err);

            setError("Unable to load tools.");

        }

        finally {

            setLoading(false);

        }

    }

    useEffect(() => {

        loadTools();

    }, []);

    return {

        tools,

        loading,

        error,

        refresh: loadTools,

    };

}