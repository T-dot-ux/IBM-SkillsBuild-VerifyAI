"use client";

import { useState } from "react";
import { AuthModal } from "@/components/auth/AuthModal";
import { motion } from "framer-motion";
import { ArrowRight, Shield, MessageSquare, Mic } from "lucide-react";
import { useRouter } from "next/navigation";
import { TeamSection } from "@/components/TeamSection";

export default function Home() {
  const [showAuth, setShowAuth] = useState(false);
  const router = useRouter();

  const handleSuccess = (token: string) => {
    localStorage.setItem("token", token);
    router.push("/dashboard");
  };

  return (
    <main className="min-h-screen w-full overflow-x-hidden bg-yellow-400 font-sans selection:bg-black selection:text-white flex flex-col items-center justify-center pt-24 pb-24">
      {showAuth && (
        <AuthModal onClose={() => setShowAuth(false)} onSuccess={handleSuccess} />
      )}
      
      <div className="fixed top-0 left-0 w-full p-6 flex justify-between items-center border-b-8 border-black bg-white z-50">
        <div className="text-3xl font-black tracking-tighter uppercase flex items-center gap-2">
          <Shield className="w-8 h-8 text-red-500" />
          VerifyAI
        </div>
        <button 
          onClick={() => setShowAuth(true)}
          className="px-6 py-2 bg-blue-500 text-white font-black uppercase tracking-wider rounded-lg border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 hover:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)] transition-all"
        >
          ENTER SYSTEM
        </button>
      </div>

      <div className="max-w-5xl mx-auto mt-10 grid grid-cols-1 md:grid-cols-2 gap-12 items-center px-6">
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, type: "spring", bounce: 0.5 }}
          className="space-y-8"
        >
          <h1 className="text-6xl md:text-8xl font-black text-black leading-[0.9] uppercase drop-shadow-[4px_4px_0px_rgba(255,255,255,1)]">
            YOUR DIGITAL TRUST COPILOT
          </h1>
          <p className="text-2xl font-bold text-black border-l-8 border-red-500 pl-6 py-2">
            AI-powered document and web verification. Speak in English or Hindi to instantly detect scams.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 pt-4">
            <button 
              onClick={() => setShowAuth(true)}
              className="group flex items-center justify-center gap-2 px-8 py-5 bg-green-400 text-black text-xl font-black uppercase rounded-xl border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:translate-y-1 hover:translate-x-1 hover:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)] transition-all"
            >
              Start Mission <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
            </button>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2, type: "spring" }}
          className="relative bg-white border-8 border-black rounded-3xl p-8 shadow-[16px_16px_0px_0px_rgba(0,0,0,1)]"
        >
          <div className="absolute -top-6 -right-6 w-20 h-20 bg-pink-500 rounded-full border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center animate-bounce">
            <Mic className="w-10 h-10 text-white" />
          </div>
          
          <div className="space-y-6">
            <div className="flex gap-4 items-start">
              <div className="w-12 h-12 rounded-full bg-blue-500 border-4 border-black flex-shrink-0" />
              <div className="bg-gray-100 p-4 rounded-2xl rounded-tl-none border-4 border-black font-bold text-black">
                "Hi, is this website safe? www.freemoney.com"
              </div>
            </div>
            
            <div className="flex gap-4 items-start flex-row-reverse">
              <div className="w-12 h-12 rounded-full bg-red-500 border-4 border-black flex-shrink-0 flex items-center justify-center">
                🤖
              </div>
              <div className="bg-green-100 p-4 rounded-2xl rounded-tr-none border-4 border-black font-bold text-black">
                CRITICAL ALERT! That site exhibits multiple phishing indicators. Do not proceed.
              </div>
            </div>
            
            <div className="flex gap-4 items-start">
              <div className="w-12 h-12 rounded-full bg-blue-500 border-4 border-black flex-shrink-0" />
              <div className="bg-gray-100 p-4 rounded-2xl rounded-tl-none border-4 border-black font-bold text-black">
                "क्या यह QR कोड सुरक्षित है?" (Is this QR code safe?)
              </div>
            </div>
          </div>
        </motion.div>
      </div>
      
      {/* Team Section */}
      <TeamSection />

      {/* Footer Banner */}
      <div className="fixed bottom-0 w-full overflow-hidden bg-black text-white py-3 border-t-8 border-black font-black text-xl whitespace-nowrap z-0">
        <motion.div 
          animate={{ x: ["0%", "-50%"] }} 
          transition={{ repeat: Infinity, duration: 15, ease: "linear" }}
          className="inline-block"
        >
          VERIFYAI • NO SCAMS • 100% SECURE • AGENTIC AI • MULTI-LINGUAL VOICE SUPPORT • VERIFYAI • NO SCAMS • 100% SECURE • AGENTIC AI • MULTI-LINGUAL VOICE SUPPORT • 
        </motion.div>
      </div>
    </main>
  );
}
