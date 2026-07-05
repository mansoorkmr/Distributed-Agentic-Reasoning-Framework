import { useEffect, useState } from "react";

import {
    getMemory,
    type MemoryResponse,
} from "../services/memory";

export function useMemory() {

    const [memory, setMemory] = useState<MemoryResponse | null>(null);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState<string | null>(null);

    async function loadMemory() {

        setLoading(true);

        setError(null);

        try {

            const response = await getMemory();

            setMemory(response);

        }

        catch (err) {

            console.error(err);

            setError("Unable to load memory.");

        }

        finally {

            setLoading(false);

        }

    }

    useEffect(() => {

        loadMemory();

    }, []);

    return {

        memory,

        loading,

        error,

        refresh: loadMemory,

    };

}