import DashboardLayout from "../layouts/DashboardLayout";
import ChatPanel from "../components/chat/ChatPanel";
import AgentPanel from "../components/agents/AgentPanel";
import MemoryPanel from "../components/memory/MemoryPanel";
import ToolPanel from "../components/tools/ToolPanel";

function Dashboard() {
    return (
        <DashboardLayout>
            <div className="grid gap-6 md:grid-cols-2">
                <ChatPanel />
                <AgentPanel />
                <MemoryPanel />
                <ToolPanel />
            </div>
        </DashboardLayout>
    );
}

export default Dashboard;