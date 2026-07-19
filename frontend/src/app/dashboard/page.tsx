"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion, useMotionValue, useTransform, animate } from "framer-motion";
import { ShieldCheck, AlertTriangle, Info, CheckCircle, FileText, Activity } from "lucide-react";
import { verifyApi } from "@/lib/api";
import { MascotChat } from "@/components/animations/MascotChat";

function ScoreCounter({ score, color }: { score: number, color: string }) {
    const count = useMotionValue(0);
    const rounded = useTransform(count, Math.round);

    useEffect(() => {
        const animation = animate(count, score, { duration: 1.5, ease: "easeOut" });
        return animation.stop;
    }, [score, count]);

    return (
        <div className="text-6xl font-black" style={{ color: color || '#10B981' }}>
            <motion.span>{rounded}</motion.span><span className="text-2xl text-slate-500">/100</span>
        </div>
    );
}

type ReasoningNode = {
    agent: string;
    finding: string;
    impact: string;
};

type VerdictData = {
    level: string;
    color: string;
    mascot_state: string;
};

type JobData = {
    job_id: string;
    filename: string;
    status: string;
    trust_score: number;
    summary: string;
    recommendation: string;
    reasoning_tree?: ReasoningNode[];
    verdict?: VerdictData;
};

function DashboardContent() {
    const searchParams = useSearchParams();
    const jobId = searchParams.get("job");
    const [data, setData] = useState<JobData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!jobId) {
            setLoading(false);
            return;
        }

        const fetchJob = async () => {
            try {
                const res = await verifyApi.getJobStatus(jobId);
                setData(res);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchJob();
    }, [jobId]);

    if (loading) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white"><Activity className="w-8 h-8 animate-spin text-blue-500" /></div>;

    if (!jobId) return <GlobalDashboard />;

    if (!data) return (
        <div className="min-h-screen flex flex-col items-center justify-center p-6 text-white space-y-4">
            <h1 className="text-3xl font-bold">Job Not Found</h1>
            <p className="text-slate-400">The verification job could not be loaded.</p>
        </div>
    );

    const vColor = data.verdict?.color || "#3B82F6";
    // Convert hex to rgb for rgba backgrounds
    const hex2rgb = (hex: string) => {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : '59, 130, 246';
    };
    const rgbColor = hex2rgb(vColor);

    return (
        <div className="min-h-screen animated-bg p-6 md:p-12 text-white overflow-hidden relative pt-24">
            {/* Background 3D glowing asset replacement */}
            <div className="absolute top-0 right-0 w-full lg:w-1/2 h-full opacity-40 pointer-events-none z-0 flex items-center justify-center">
                <div className="w-96 h-96 blur-[100px] rounded-full animate-pulse" style={{ backgroundColor: `rgba(${rgbColor}, 0.1)` }} />
                <div className="absolute w-64 h-64 bg-purple-500/10 blur-[80px] rounded-full animate-pulse delay-700 ml-40 mt-40" />
            </div>
            
            <div className="max-w-5xl mx-auto space-y-8 relative z-10">
                
                <header className="flex justify-between items-end border-b border-slate-800 pb-6">
                    <div>
                        <h1 className="text-4xl font-bold">Verification Report</h1>
                        <p className="text-slate-400 mt-2 flex items-center gap-2">
                            <FileText className="w-4 h-4" /> {data.filename}
                        </p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-slate-400 uppercase tracking-widest font-semibold mb-1">Trust Score</p>
                        <ScoreCounter score={data.trust_score} color={vColor} />
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Summary Card */}
                    <div className="col-span-1 md:col-span-2 bg-glass rounded-2xl p-6" style={{ boxShadow: `0 0 20px rgba(${rgbColor}, 0.15)` }}>
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            <Info className="w-5 h-5" style={{ color: vColor }} /> Executive Summary
                        </h2>
                        <p className="text-slate-300 text-lg leading-relaxed">{data.summary}</p>
                        
                        <div className="mt-6 p-4 rounded-xl border" style={{ backgroundColor: `rgba(${rgbColor}, 0.1)`, borderColor: `rgba(${rgbColor}, 0.3)`, color: vColor }}>
                            <span className="font-bold uppercase text-xs tracking-wider opacity-70 block mb-1">Recommendation</span>
                            {data.recommendation}
                        </div>
                    </div>

                    {/* Breakdown */}
                    <div className="bg-glass rounded-2xl p-6 space-y-6">
                        <h2 className="text-xl font-semibold mb-4 text-white">Risk Factors</h2>
                        
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-400">Critical / High Risks</span>
                                <span className="font-mono text-red-400">{data.reasoning_tree?.filter(e => e.impact === "CRITICAL" || e.impact === "HIGH").length || 0}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-400">Moderate Risks</span>
                                <span className="font-mono text-yellow-400">{data.reasoning_tree?.filter(e => e.impact === "MODERATE").length || 0}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-slate-400">Positive Indicators</span>
                                <span className="font-mono text-emerald-400">{data.reasoning_tree?.filter(e => e.impact === "POSITIVE").length || 0}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Evidence List */}
                <div className="bg-glass rounded-2xl p-6">
                    <h2 className="text-xl font-semibold mb-6">Extracted Evidence Log</h2>
                    
                    {(!data.reasoning_tree || data.reasoning_tree.length === 0) ? (
                        <p className="text-slate-500 italic">No specific reasoning extracted.</p>
                    ) : (
                        <div className="space-y-3">
                            {data.reasoning_tree.map((ev, i) => (
                                <motion.div 
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.1 * i }}
                                    key={i} 
                                    className={`p-4 rounded-xl flex gap-4 transition-all hover:scale-[1.01] ${ev.impact === 'CRITICAL' ? 'bg-red-950/40 border border-red-900/50' : ev.impact === 'HIGH' ? 'bg-orange-950/40 border border-orange-900/50' : ev.impact === 'MODERATE' ? 'bg-yellow-950/40 border border-yellow-900/50' : 'bg-emerald-950/40 border border-emerald-900/50'}`}>
                                    <div className="mt-1">
                                        {ev.impact === 'CRITICAL' || ev.impact === 'HIGH' ? <AlertTriangle className="w-5 h-5 text-red-500" /> : ev.impact === 'MODERATE' ? <AlertTriangle className="w-5 h-5 text-yellow-500" /> : <CheckCircle className="w-5 h-5 text-emerald-500" />}
                                    </div>
                                    <div>
                                        <p className="text-slate-400 text-xs font-bold uppercase mb-1">{ev.agent}</p>
                                        <p className="text-slate-200 text-sm leading-relaxed">{ev.finding}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}

export default function DashboardPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-white"><Activity className="w-8 h-8 animate-spin text-blue-500" /></div>}>
            <DashboardContent />
        </Suspense>
    );
}


function GlobalDashboard() {
    return (
        <div className="p-8 text-black bg-yellow-400 min-h-screen">
            <header className="mb-10 text-center">
                <h1 className="text-4xl md:text-6xl font-black uppercase tracking-tighter drop-shadow-[4px_4px_0px_rgba(255,255,255,1)]">
                    Mission Control
                </h1>
                <p className="text-xl font-bold mt-2">Chat with VerifyAI Copilot to analyze threats</p>
            </header>

            <div className="max-w-7xl mx-auto flex flex-col items-center">
                <MascotChat />
            </div>
            
            <div className="mt-16 text-center">
                <a href="/dashboard/history" className="inline-block px-8 py-4 bg-blue-500 text-white font-black text-xl uppercase rounded-xl border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 hover:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)] transition-all">
                    View Verification History
                </a>
            </div>
        </div>
    );
}
