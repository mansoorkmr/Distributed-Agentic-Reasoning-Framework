import type { AgentInfo } from "../../services/agents";

interface AgentCardProps {
    agent: AgentInfo;
}

function AgentCard({
    agent,
}: AgentCardProps) {

    return (

        <div className="rounded-xl border border-slate-700 bg-slate-800 p-5 shadow-sm">

            <div className="mb-3 flex items-center justify-between">

                <h3 className="text-lg font-semibold text-white">

                    {agent.name}

                </h3>

                <span className="rounded-full bg-green-600 px-3 py-1 text-xs font-medium text-white">

                    {agent.status}

                </span>

            </div>

            <p className="mb-4 text-sm text-slate-300">

                {agent.description}

            </p>

            <div className="mb-3 text-sm text-slate-400">

                <strong>ID:</strong> {agent.id}

            </div>

            <div className="mb-4 text-sm text-slate-400">

                <strong>Version:</strong> {agent.version}

            </div>

            <div>

                <h4 className="mb-2 font-medium text-white">

                    Capabilities

                </h4>

                <div className="flex flex-wrap gap-2">

                    {agent.capabilities.map(

                        capability => (

                            <span
                                key={capability}
                                className="rounded bg-blue-600 px-2 py-1 text-xs text-white"
                            >

                                {capability}

                            </span>

                        ),

                    )}

                </div>

            </div>

        </div>

    );

}

export default AgentCard;