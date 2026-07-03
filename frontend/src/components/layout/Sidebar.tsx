import {
    Bot,
    Brain,
    Wrench,
    Play,
    MessageSquare,
} from "lucide-react";

function Sidebar() {

    return (

        <aside className="w-64 bg-slate-950 border-r border-slate-800">

            <div className="p-6">

                <h1 className="text-2xl font-bold">

                    DARF

                </h1>

                <p className="text-sm text-slate-400">

                    Agent Dashboard

                </p>

            </div>

            <nav className="space-y-2 px-4">

                <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-slate-800">

                    <MessageSquare size={20} />

                    Chat

                </button>

                <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-slate-800">

                    <Bot size={20} />

                    Agents

                </button>

                <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-slate-800">

                    <Brain size={20} />

                    Memory

                </button>

                <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-slate-800">

                    <Wrench size={20} />

                    Tools

                </button>

                <button className="flex w-full items-center gap-3 rounded-lg p-3 hover:bg-slate-800">

                    <Play size={20} />

                    Execute

                </button>

            </nav>

        </aside>

    );

}

export default Sidebar;