import DashboardLayout from "../layouts/DashboardLayout";
import ChatPanel from "../components/chat/ChatPanel";

function Dashboard() {

    return (

        <DashboardLayout>

            <div className="grid gap-6 md:grid-cols-2">

                <ChatPanel />

                <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">

                    Agent Panel

                </div>

                <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">

                    Memory Panel

                </div>

                <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">

                    Tool Panel

                </div>

            </div>

        </DashboardLayout>

    );

}

export default Dashboard;