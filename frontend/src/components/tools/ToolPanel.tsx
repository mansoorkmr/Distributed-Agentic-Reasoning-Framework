import ToolCard from "./ToolCard";

import { useTools } from "../../hooks/useTools";

function ToolPanel() {

    const {

        tools,

        loading,

        error,

    } = useTools();

    if (loading) {

        return (

            <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 text-slate-300">

                Loading tools...

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

    if (!tools) {

        return (

            <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 text-slate-300">

                No tools available.

            </div>

        );

    }

    return (

        <div className="rounded-xl border border-slate-700 bg-slate-800 p-5">

            <div className="mb-5 flex items-center justify-between">

                <h2 className="text-xl font-semibold text-white">

                    Tool Panel

                </h2>

                <span className="rounded-full bg-blue-600 px-3 py-1 text-sm text-white">

                    {tools.count} Tools

                </span>

            </div>

            <div className="mb-5">

                <h3 className="mb-2 text-sm font-medium text-slate-300">

                    Capabilities

                </h3>

                <div className="flex flex-wrap gap-2">

                    {tools.capabilities.map(capability => (

                        <span
                            key={capability}
                            className="rounded bg-slate-700 px-2 py-1 text-xs text-white"
                        >

                            {capability}

                        </span>

                    ))}

                </div>

            </div>

            {

                tools.tools.length === 0

                    ? (

                        <div className="rounded-lg border border-dashed border-slate-600 p-6 text-center text-slate-400">

                            No runtime tools are currently registered.

                        </div>

                    )

                    : (

                        <div className="grid gap-4">

                            {

                                tools.tools.map(

                                    tool => (

                                        <ToolCard

                                            key={tool.name}

                                            tool={tool}

                                        />

                                    ),

                                )

                            }

                        </div>

                    )

            }

        </div>

    );

}

export default ToolPanel;