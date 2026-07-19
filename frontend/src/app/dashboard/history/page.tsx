"use client";

import { useState, useEffect } from "react";
import { FileText, Loader2, ArrowRight } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

type HistoryItem = {
    id: string;
    filename: string;
    status: string;
    trust_score: number | null;
    created_at: string;
};

export default function HistoryPage() {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            const token = localStorage.getItem("token");
            if (!token) {
                setLoading(false);
                return;
            }
            try {
                const res = await fetch("http://localhost:8000/api/history", {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    setHistory(data);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    return (
        <div className="min-h-screen bg-pink-400 p-8 text-black selection:bg-black selection:text-white">
            <header className="mb-12 border-b-8 border-black pb-6 pt-10">
                <h1 className="text-4xl md:text-6xl font-black uppercase tracking-tighter drop-shadow-[4px_4px_0px_rgba(255,255,255,1)]">
                    Verification Log
                </h1>
                <p className="text-xl font-bold mt-2 bg-white inline-block px-4 py-1 border-4 border-black rounded-lg shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    Every file, link, and code you've checked.
                </p>
            </header>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <Loader2 className="w-12 h-12 animate-spin text-black" />
                </div>
            ) : history.length === 0 ? (
                <div className="text-center bg-white p-12 border-8 border-black rounded-3xl shadow-[16px_16px_0px_0px_rgba(0,0,0,1)]">
                    <h2 className="text-3xl font-black mb-4">No records found.</h2>
                    <p className="text-lg font-bold mb-8">Start verifying links and documents with VerifyAI Copilot.</p>
                    <Link href="/dashboard" className="px-8 py-4 bg-blue-500 text-white font-black text-xl uppercase rounded-xl border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 hover:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)] transition-all">
                        Go to Mission Control
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {history.map((item, i) => (
                        <motion.div 
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            key={item.id} 
                            className="bg-white border-8 border-black rounded-3xl p-6 shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] flex flex-col justify-between"
                        >
                            <div>
                                <div className="flex justify-between items-start mb-6">
                                    <div className="w-12 h-12 bg-purple-400 border-4 border-black rounded-xl flex items-center justify-center">
                                        <FileText className="w-6 h-6 text-black" />
                                    </div>
                                    <div className={`px-4 py-1 border-4 border-black rounded-full font-black text-sm uppercase ${
                                        !item.trust_score ? 'bg-gray-200' :
                                        item.trust_score < 50 ? 'bg-red-400 text-black' : 
                                        item.trust_score < 80 ? 'bg-yellow-400 text-black' : 
                                        'bg-green-400 text-black'
                                    }`}>
                                        {item.status}
                                    </div>
                                </div>
                                <h3 className="text-2xl font-black mb-2 truncate" title={item.filename}>{item.filename}</h3>
                                <p className="text-gray-600 font-bold mb-6">
                                    {new Date(item.created_at).toLocaleDateString()}
                                </p>
                            </div>
                            
                            <div className="flex justify-between items-center pt-4 border-t-4 border-black">
                                <div className="font-black text-3xl">
                                    {item.trust_score !== null ? `${item.trust_score}/100` : '--/100'}
                                </div>
                                <Link 
                                    href={`/dashboard?job=${item.id}`} 
                                    className="p-3 bg-black text-white rounded-xl hover:bg-gray-800 transition-colors"
                                >
                                    <ArrowRight className="w-6 h-6" />
                                </Link>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
