import DashboardLayout from "../layouts/DashboardLayout";
import ChatPanel from "../components/chat/ChatPanel";
import AgentPanel from "../components/agents/AgentPanel";
import MemoryPanel from "../components/memory/MemoryPanel";

function Dashboard() {
    return (
        <DashboardLayout>
            <div className="grid gap-6 md:grid-cols-2">
                <ChatPanel />
                <AgentPanel />
                <MemoryPanel />
                <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
                    Tool Panel
                </div>
            </div>
        </DashboardLayout>
    );
}

export default Dashboard;