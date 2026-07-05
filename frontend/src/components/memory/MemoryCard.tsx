import type { MemoryResponse } from "../../services/memory";

interface MemoryCardProps {
    memory: MemoryResponse;
}

function MemoryCard({
    memory,
}: MemoryCardProps) {

    return (

        <div className="rounded-xl border border-slate-700 bg-slate-800 p-5 shadow-sm">

            <div className="mb-4 flex items-center justify-between">

                <h3 className="text-lg font-semibold text-white">

                    Memory Overview

                </h3>

                <span className="rounded-full bg-green-600 px-3 py-1 text-xs font-medium text-white">

                    {memory.status}

                </span>

            </div>

            <div className="space-y-3 text-sm text-slate-300">

                <div className="flex justify-between">

                    <span>Vector Store</span>

                    <span className="font-medium">

                        {memory.vector_store}

                    </span>

                </div>

                <div className="flex justify-between">

                    <span>Embedding Model</span>

                    <span className="font-medium">

                        {memory.embedding_model}

                    </span>

                </div>

                <div className="flex justify-between">

                    <span>Top-K</span>

                    <span className="font-medium">

                        {memory.top_k}

                    </span>

                </div>

                <div className="flex justify-between">

                    <span>Memory Size</span>

                    <span className="font-medium">

                        {memory.memory_size}

                    </span>

                </div>

                <div className="flex justify-between">

                    <span>Variables</span>

                    <span className="font-medium">

                        {memory.metrics.variables}

                    </span>

                </div>

                <div className="flex justify-between">

                    <span>Outputs</span>

                    <span className="font-medium">

                        {memory.metrics.outputs}

                    </span>

                </div>

            </div>

        </div>

    );

}

export default MemoryCard;