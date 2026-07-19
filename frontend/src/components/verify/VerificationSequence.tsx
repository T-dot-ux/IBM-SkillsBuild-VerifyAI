"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ScanSearch, FileText, Cpu, ShieldAlert, FileCheck } from "lucide-react";

const STEPS = [
  { id: "master", label: "Master Orchestrator Initializing", icon: Cpu },
  { id: "input", label: "Input Intelligence Agent (Extraction)", icon: FileText },
  { id: "threat_source", label: "Threat & Source Agents (Analysis)", icon: ShieldAlert },
  { id: "evidence", label: "Evidence Verification Agent", icon: ScanSearch },
  { id: "decision", label: "Decision Agent (Finalizing)", icon: FileCheck },
];

export const VerificationSequence = ({ onComplete }: { onComplete: () => void }) => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Mocking the sequence for the UI demo.
    // In production, this would subscribe to WebSockets/SSE from the FastAPI Celery backend.
    if (currentStep < STEPS.length) {
      const timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 2000); // 2 seconds per step for demonstration
      return () => clearTimeout(timer);
    } else {
      onComplete();
    }
  }, [currentStep, onComplete]);

  return (
    <div className="w-full max-w-3xl mx-auto bg-white/5 border border-white/10 backdrop-blur-xl rounded-3xl p-8 md:p-12">
      <h2 className="text-2xl font-bold text-white mb-8 text-center">Verification in Progress</h2>
      
      <div className="space-y-6 relative">
        {/* Progress Line */}
        <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-white/10 z-0 hidden md:block" />

        {STEPS.map((step, index) => {
          const isActive = index === currentStep;
          const isPast = index < currentStep;
          const Icon = step.icon;

          return (
            <div key={step.id} className="relative z-10 flex items-center gap-6">
              <motion.div
                initial={false}
                animate={{
                  backgroundColor: isActive ? "#0066ff" : isPast ? "#00ffff" : "rgba(255,255,255,0.05)",
                  borderColor: isActive || isPast ? "transparent" : "rgba(255,255,255,0.1)",
                  scale: isActive ? 1.1 : 1,
                }}
                className="w-12 h-12 rounded-full border-2 flex items-center justify-center shrink-0 shadow-lg"
              >
                <Icon className={`w-5 h-5 ${isActive || isPast ? "text-white" : "text-slate-500"}`} />
              </motion.div>
              
              <div className="flex-1">
                <motion.p
                  animate={{
                    color: isActive ? "#ffffff" : isPast ? "#94a3b8" : "#475569",
                    fontWeight: isActive ? 700 : 500,
                  }}
                  className="text-lg"
                >
                  {step.label}
                </motion.p>
                
                <AnimatePresence>
                  {isActive && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-2 text-sm text-primary overflow-hidden"
                    >
                      <div className="flex items-center gap-2">
                        <div className="flex space-x-1">
                          <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0 }} className="w-1.5 h-1.5 bg-primary rounded-full" />
                          <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.2 }} className="w-1.5 h-1.5 bg-primary rounded-full" />
                          <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.4 }} className="w-1.5 h-1.5 bg-primary rounded-full" />
                        </div>
                        Processing module...
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
