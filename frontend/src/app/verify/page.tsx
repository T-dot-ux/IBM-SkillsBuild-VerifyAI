"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, Loader2, ShieldCheck } from "lucide-react";
import { verifyApi } from "@/lib/api";
import { InteractiveCube } from "@/components/animations/InteractiveCube";
import { AnimatedTiles } from "@/components/animations/AnimatedTiles";
import { UploadZone } from "@/components/upload/UploadZone";
import { Reveal } from "@/components/animations/Reveal";

export default function VerifyPage() {
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [jobId, setJobId] = useState<string | null>(null);
    const [status, setStatus] = useState<string>("IDLE");
    const router = useRouter();

    const handleUpload = async (uploadedFile: File) => {
        setFile(uploadedFile);
        try {
            setIsUploading(true);
            const res = await verifyApi.uploadDocument(uploadedFile);
            setJobId(res.job_id);
            setStatus("PENDING");
            setIsUploading(false);
        } catch (err) {
            console.error(err);
            alert("Upload failed. Please check the backend connection.");
            setIsUploading(false);
        }
    };

    // Polling logic
    useEffect(() => {
        if (!jobId || status === "COMPLETED" || status === "FAILED") return;
        
        const interval = setInterval(async () => {
            try {
                const res = await verifyApi.getJobStatus(jobId);
                setStatus(res.status);
                
                if (res.status === "COMPLETED") {
                    clearInterval(interval);
                    // Redirect to dashboard with Job ID
                    router.push(`/dashboard?job=${jobId}`);
                } else if (res.status === "FAILED") {
                    clearInterval(interval);
                    alert("Verification failed during processing.");
                }
            } catch (err) {
                console.error("Polling error", err);
            }
        }, 3000);
        
        return () => clearInterval(interval);
    }, [jobId, status, router]);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-6 text-white pt-24 overflow-hidden relative">
            {/* Spreading Tiles Background */}
            <AnimatedTiles />
            
            <div className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center z-10">
                {/* Left Column: 3D Asset & Text */}
                <div className="space-y-6">
                    <Reveal>
                        <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400 leading-tight">
                            Verify a Digital Artifact
                        </h1>
                    </Reveal>
                    <Reveal delay={0.2}>
                        <p className="text-lg text-slate-400">
                            Upload a job offer, invoice, or certificate. Our AI will analyze it for authenticity using multi-agent verification.
                        </p>
                    </Reveal>
                    <Reveal delay={0.4}>
                        <div className="h-[400px] w-full rounded-3xl overflow-hidden bg-white/5 border border-white/10 relative mt-8 flex items-center justify-center shadow-[0_0_50px_rgba(0,255,255,0.1)]">
                            {/* Animated CSS Grid & Floating Elements instead of broken Spline */}
                            <div className="absolute inset-0 grid-bg opacity-30" />
                            <div className="absolute w-64 h-64 bg-cyan-500/20 blur-3xl rounded-full animate-pulse" />
                            <div className="absolute w-48 h-48 bg-purple-500/20 blur-3xl rounded-full animate-pulse delay-700 ml-32 mt-32" />
                            <div className="relative z-10 flex items-center justify-center pt-8">
                                <InteractiveCube />
                            </div>
                        </div>
                    </Reveal>
                </div>

                {/* Right Column: Upload Zone */}
                <Reveal delay={0.3}>
                    {!jobId ? (
                        <div className="flex justify-center mt-8 lg:mt-0">
                           <UploadZone onUpload={handleUpload} />
                        </div>
                    ) : (
                        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 space-y-6 shadow-2xl backdrop-blur-xl">
                            <h2 className="text-2xl font-semibold">Analyzing Artifact...</h2>
                            
                            <div className="flex flex-col space-y-4">
                                <StatusStep active={status === "PENDING" || status === "SCANNING" || status === "EXTRACTING" || status === "ANALYZING" || status === "COMPLETED"} current={status === "PENDING"} label="Initializing Job" />
                                <StatusStep active={status === "SCANNING" || status === "EXTRACTING" || status === "ANALYZING" || status === "COMPLETED"} current={status === "SCANNING" || status === "EXTRACTING"} label="Extracting Text & OCR" />
                                <StatusStep active={status === "ANALYZING" || status === "COMPLETED"} current={status === "ANALYZING"} label="AI Semantic Analysis & Rule Engine" />
                                <StatusStep active={status === "COMPLETED"} current={status === "COMPLETED"} label="Finalizing Trust Score" />
                            </div>
                            
                            <p className="text-sm text-slate-500 animate-pulse pt-4">This usually takes about 10-20 seconds...</p>
                        </div>
                    )}
                </Reveal>
            </div>
        </div>
    );
}

function StatusStep({ active, current, label }: { active: boolean, current: boolean, label: string }) {
    return (
        <div className={`flex items-center gap-4 p-4 rounded-xl transition-all ${active ? "bg-blue-900/20 border border-blue-800/50" : "opacity-50"}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${current ? "bg-blue-500 animate-pulse" : active ? "bg-emerald-500" : "bg-slate-700"}`}>
                {active && !current ? <ShieldCheck className="w-5 h-5 text-white" /> : current ? <Loader2 className="w-5 h-5 text-white animate-spin" /> : <div className="w-2 h-2 rounded-full bg-slate-400" />}
            </div>
            <span className={`font-medium ${current ? "text-blue-300" : active ? "text-emerald-300" : "text-slate-500"}`}>{label}</span>
        </div>
    );
}
