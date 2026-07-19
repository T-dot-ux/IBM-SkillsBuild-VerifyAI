import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/50 backdrop-blur-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <ShieldCheck className="w-8 h-8 text-cyan-400 group-hover:scale-110 transition-transform" />
          <span className="font-bold text-xl tracking-tight text-white">VerifyAI</span>
        </Link>
        
        <div className="hidden md:flex items-center gap-8">
          <Link href="/#features" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
            How it works
          </Link>
          <Link href="/dashboard" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
            Dashboard
          </Link>
        </div>

        <Link 
          href="/verify" 
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-lg transition-all shadow-[0_0_15px_-3px_rgba(37,99,235,0.6)] hover:shadow-[0_0_25px_-3px_rgba(37,99,235,0.8)]"
        >
          Verify Now
        </Link>
      </div>
    </nav>
  );
}
