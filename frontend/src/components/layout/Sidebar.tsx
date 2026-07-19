import Link from "next/link";
import { LayoutDashboard, History } from "lucide-react";

export function Sidebar() {
    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-yellow-400 border-r-8 border-black p-6 flex flex-col z-50 text-black">
            <div className="flex items-center gap-3 mb-10 border-b-8 border-black pb-6">
                <div className="w-10 h-10 rounded-xl bg-blue-500 border-4 border-black flex items-center justify-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    <ShieldCheckIcon className="text-white w-6 h-6" />
                </div>
                <span className="text-2xl font-black uppercase tracking-tight">VerifyAI</span>
            </div>

            <nav className="flex-1 space-y-4">
                <NavItem href="/dashboard" icon={<LayoutDashboard />} label="Dashboard" />
                <NavItem href="/dashboard/history" icon={<History />} label="History" />
            </nav>
        </aside>
    );
}

function NavItem({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
    return (
        <Link href={href} className="flex items-center gap-3 px-4 py-3 bg-white text-black font-black uppercase border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 hover:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)] transition-all rounded-xl">
            <div className="w-5 h-5">{icon}</div>
            <span className="text-sm">{label}</span>
        </Link>
    );
}

function ShieldCheckIcon(props: any) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="m9 12 2 2 4-4" />
        </svg>
    );
}
