import AgentCard from "./AgentCard";

import { useAgents } from "../../hooks/useAgents";

function AgentPanel() {

    const {

        agents,

        loading,

        error,

    } = useAgents();

    if (loading) {

        return (

            <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 text-slate-300">

                Loading registered agents...

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

    return (

        <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">

            <div className="mb-6 flex items-center justify-between">

                <h2 className="text-2xl font-bold text-white">

                    Registered Agents

                </h2>

                <span className="rounded-full bg-blue-600 px-3 py-1 text-sm text-white">

                    {agents.length} Agents

                </span>

            </div>

            <div className="grid gap-4">

                {

                    agents.map(

                        agent => (

                            <AgentCard

                                key={agent.id}

                                agent={agent}

                            />

                        ),

                    )

                }

            </div>

        </div>

    );

}

export default AgentPanel;