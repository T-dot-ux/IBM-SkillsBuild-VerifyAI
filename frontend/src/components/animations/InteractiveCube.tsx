"use client";

import { motion } from "framer-motion";
import { useState } from "react";

export function InteractiveCube() {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="relative w-48 h-48 perspective-1000 cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <motion.div
        className="w-full h-full relative preserve-3d"
        animate={{
          rotateX: isHovered ? [0, 180, 360] : [0, 360],
          rotateY: isHovered ? [0, 360, 0] : [0, 360],
        }}
        transition={{
          duration: isHovered ? 2 : 12,
          ease: "linear",
          repeat: Infinity,
        }}
      >
        {/* Front */}
        <div className="absolute inset-0 bg-cyan-500/10 border-2 border-cyan-400/60 flex items-center justify-center backdrop-blur-md translate-z-24 shadow-[0_0_30px_rgba(34,211,238,0.4)]">
          <div className="w-12 h-12 border border-cyan-300/80 rounded-full animate-pulse" />
        </div>
        {/* Back */}
        <div className="absolute inset-0 bg-purple-500/10 border-2 border-purple-400/60 flex items-center justify-center backdrop-blur-md -translate-z-24 shadow-[0_0_30px_rgba(168,85,247,0.4)]">
          <div className="w-12 h-12 border border-purple-300/80 rounded-full animate-pulse" />
        </div>
        {/* Right */}
        <div className="absolute inset-0 bg-emerald-500/10 border-2 border-emerald-400/60 flex items-center justify-center backdrop-blur-md rotate-y-90 translate-x-24 shadow-[0_0_30px_rgba(16,185,129,0.4)]">
          <div className="w-12 h-12 border border-emerald-300/80 rounded-full animate-pulse" />
        </div>
        {/* Left */}
        <div className="absolute inset-0 bg-blue-500/10 border-2 border-blue-400/60 flex items-center justify-center backdrop-blur-md -rotate-y-90 -translate-x-24 shadow-[0_0_30px_rgba(59,130,246,0.4)]">
          <div className="w-12 h-12 border border-blue-300/80 rounded-full animate-pulse" />
        </div>
        {/* Top */}
        <div className="absolute inset-0 bg-cyan-500/10 border-2 border-cyan-400/60 flex items-center justify-center backdrop-blur-md rotate-x-90 -translate-y-24 shadow-[0_0_30px_rgba(34,211,238,0.4)]">
          <div className="w-12 h-12 border border-cyan-300/80 rounded-full animate-pulse" />
        </div>
        {/* Bottom */}
        <div className="absolute inset-0 bg-purple-500/10 border-2 border-purple-400/60 flex items-center justify-center backdrop-blur-md -rotate-x-90 translate-y-24 shadow-[0_0_30px_rgba(168,85,247,0.4)]">
          <div className="w-12 h-12 border border-purple-300/80 rounded-full animate-pulse" />
        </div>
      </motion.div>
      <style jsx global>{`
        .perspective-1000 { perspective: 1000px; }
        .preserve-3d { transform-style: preserve-3d; }
        .translate-z-24 { transform: translateZ(6rem); }
        .-translate-z-24 { transform: rotateY(180deg) translateZ(6rem); }
        .rotate-y-90 { transform: rotateY(90deg); }
        .-rotate-y-90 { transform: rotateY(-90deg); }
        .rotate-x-90 { transform: rotateX(90deg); }
        .-rotate-x-90 { transform: rotateX(-90deg); }
      `}</style>
    </div>
  );
}
