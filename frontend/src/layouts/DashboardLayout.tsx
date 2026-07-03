import type { ReactNode } from "react";

import Sidebar from "../components/layout/Sidebar";
import Header from "../components/layout/Header";

interface DashboardLayoutProps {
    children: ReactNode;
}

function DashboardLayout({
    children,
}: DashboardLayoutProps) {
    return (
        <div className="flex h-screen bg-slate-900 text-white">

            <Sidebar />

            <div className="flex flex-1 flex-col">

                <Header />

                <main className="flex-1 overflow-auto p-6">
                    {children}
                </main>

            </div>

        </div>
    );
}

export default DashboardLayout;