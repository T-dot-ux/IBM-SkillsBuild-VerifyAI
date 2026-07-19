import Link from "next/link";
import { ShieldCheck, MessageCircle, Mail, Globe } from "lucide-react";

export function Footer() {
  return (
    <footer className="w-full bg-slate-950 border-t border-white/10 pt-16 pb-8 px-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        
        <div className="md:col-span-2 space-y-4">
          <Link href="/" className="flex items-center gap-2 group w-fit">
            <ShieldCheck className="w-8 h-8 text-cyan-400 group-hover:scale-110 transition-transform" />
            <span className="font-bold text-xl tracking-tight text-white">VerifyAI</span>
          </Link>
          <p className="text-slate-400 max-w-sm">
            The ultimate verification engine to combat digital fraud using multi-agent AI architecture.
          </p>
        </div>

        <div className="space-y-4">
          <h4 className="text-white font-semibold">Product</h4>
          <ul className="space-y-2">
            <li><Link href="/verify" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">Start Verification</Link></li>
            <li><Link href="/dashboard" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">Dashboard</Link></li>
            <li><Link href="/#features" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">Features</Link></li>
          </ul>
        </div>

        <div className="space-y-4">
          <h4 className="text-white font-semibold">Legal</h4>
          <ul className="space-y-2">
            <li><Link href="#" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">Privacy Policy</Link></li>
            <li><Link href="#" className="text-slate-400 hover:text-cyan-400 transition-colors text-sm">Terms of Service</Link></li>
          </ul>
        </div>
      </div>

      <div className="max-w-7xl mx-auto border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="text-slate-500 text-sm">
          &copy; {new Date().getFullYear()} VerifyAI. All rights reserved.
        </p>
        <div className="flex gap-4">
          <Link href="#" className="text-slate-400 hover:text-white transition-colors">
            <MessageCircle className="w-5 h-5" />
          </Link>
          <Link href="#" className="text-slate-400 hover:text-white transition-colors">
            <Mail className="w-5 h-5" />
          </Link>
          <Link href="#" className="text-slate-400 hover:text-white transition-colors">
            <Globe className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </footer>
  );
}
