import type { ToolInfo } from "../../services/tools";

interface ToolCardProps {
    tool: ToolInfo;
}

function ToolCard({
    tool,
}: ToolCardProps) {

    return (

        <div className="rounded-lg border border-slate-700 bg-slate-800 p-4">

            <div className="flex items-center justify-between">

                <h3 className="text-white font-semibold">

                    {tool.name}

                </h3>

                <span className="rounded-full bg-green-600 px-2 py-1 text-xs text-white">

                    {tool.status}

                </span>

            </div>

            <div className="mt-3 text-sm text-slate-300">

                Category

            </div>

            <div className="font-medium text-white">

                {tool.category}

            </div>

        </div>

    );

}

export default ToolCard;