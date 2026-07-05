import MemoryCard from "./MemoryCard";

import { useMemory } from "../../hooks/useMemory";

function MemoryPanel() {

    const {

        memory,

        loading,

        error,

    } = useMemory();

    if (loading) {

        return (

            <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 text-slate-300">

                Loading memory...

            </div>

        );

    }

    if (error) {

        return (

            <div className="rounded-xl border border-red-600 bg-slate-800 p-6 text-red-400">

                {error}

            </div>

        );

    }

    if (!memory) {

        return (

            <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 text-slate-300">

                No memory available.

            </div>

        );

    }

    return (

        <MemoryCard

            memory={memory}

        />

    );

}

export default MemoryPanel;