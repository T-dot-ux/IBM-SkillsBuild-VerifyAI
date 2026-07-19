"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

type MascotState = "idle" | "working" | "success" | "warning" | "error";

interface MascotProps {
  state: MascotState;
}

export const Mascot = ({ state }: MascotProps) => {
  const [frame, setFrame] = useState(0);

  // Animation cycle loop for binks/visor scans
  useEffect(() => {
    const interval = setInterval(() => {
      setFrame((prev) => (prev + 1) % 6);
    }, 200);
    return () => clearInterval(interval);
  }, []);

  // Theme colors for neobrutalist borders/glows
  let color = "#3b82f6"; // Blue (idle)
  if (state === "warning" || state === "error") color = "#ef4444"; // Red (danger)
  if (state === "success") color = "#22c55e"; // Green (success)
  if (state === "working") color = "#f97316"; // Orange (working)

  // Motion variants for Mascot box shakes & bounces
  const variants = {
    idle: {
      y: [0, -5, 0],
      transition: { duration: 3, repeat: Infinity, ease: "easeInOut" }
    },
    working: {
      y: [0, -8, 0],
      scale: [1, 1.05, 1],
      transition: { duration: 0.6, repeat: Infinity, ease: "easeInOut" }
    },
    success: {
      y: [0, -20, 0],
      scale: [1, 1.1, 1],
      rotate: [0, 5, -5, 0],
      transition: { duration: 0.8, repeat: Infinity, ease: "easeOut" }
    },
    warning: {
      x: [-4, 4, -4],
      transition: { duration: 0.2, repeat: Infinity }
    },
    error: {
      x: [-8, 8, -8],
      y: [-2, 2, -2],
      transition: { duration: 0.1, repeat: Infinity }
    }
  };

  // 10x10 Grid representation for the robot face:
  // 0 = Transparent / White
  // 1 = Theme Color (Border/Accents)
  // 2 = Dark outline / Black details
  // 3 = Visor glow (Cyan/Orange)
  const getGridMatrix = (): number[][] => {
    // Shared empty head structure template
    const base = [
      [0, 0, 0, 0, 1, 1, 0, 0, 0, 0], // Row 0: Antenna bulb
      [0, 0, 0, 0, 0, 1, 0, 0, 0, 0], // Row 1: Antenna stick
      [0, 1, 1, 1, 1, 1, 1, 1, 1, 0], // Row 2: Head top border
      [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], // Row 3:
      [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], // Row 4: Eye upper
      [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], // Row 5: Eye lower
      [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], // Row 6:
      [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], // Row 7: Mouth upper
      [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], // Row 8: Mouth lower
      [0, 1, 1, 1, 1, 1, 1, 1, 1, 0], // Row 9: Head bottom border
    ];

    if (state === "idle") {
      const isBlinking = frame === 4; // blink on frame 4
      if (isBlinking) {
        // Flat line eyes
        base[4][2] = 2; base[4][3] = 2;
        base[4][6] = 2; base[4][7] = 2;
      } else {
        // Round open eyes
        base[4][2] = 2; base[4][3] = 2;
        base[5][2] = 2; base[5][3] = 2;
        base[4][6] = 2; base[4][7] = 2;
        base[5][6] = 2; base[5][7] = 2;
      }
      // Smiling mouth
      base[7][2] = 2; base[7][7] = 2;
      base[8][3] = 2; base[8][4] = 2; base[8][5] = 2; base[8][6] = 2;
    }

    else if (state === "working") {
      // Visor scanning loop across cols 2-7
      const scanCol = 2 + (frame % 5);
      base[4][scanCol] = 3;
      base[4][scanCol + 1] = 3;
      base[5][scanCol] = 3;
      base[5][scanCol + 1] = 3;
      
      // Concentrated straight line mouth
      base[7][3] = 2; base[7][4] = 2; base[7][5] = 2; base[7][6] = 2;
    }

    else if (state === "success") {
      // Happy arches for eyes: ^ ^
      base[4][2] = 2; base[4][4] = 2;
      base[3][3] = 2;
      base[4][5] = 2; base[4][7] = 2;
      base[3][6] = 2;
      
      // Big open laughing mouth
      base[7][3] = 2; base[7][6] = 2;
      base[8][4] = 2; base[8][5] = 2;
    }

    else { // warning or error
      // Slanted angry eyebrows and eyes
      base[3][2] = 2; base[3][7] = 2;
      base[4][3] = 2; base[4][6] = 2;
      base[5][2] = 2; base[5][3] = 2;
      base[5][6] = 2; base[5][7] = 2;

      // Frowning mouth
      base[7][4] = 2; base[7][5] = 2;
      base[8][3] = 2; base[8][6] = 2;
    }

    return base;
  };

  const gridMatrix = getGridMatrix();

  return (
    <motion.div
      variants={variants}
      animate={state}
      className="relative flex flex-col items-center justify-center p-4 w-40 h-40"
    >
      {/* Outer Box with neobrutalist styling */}
      <div 
        className="grid grid-cols-10 grid-rows-10 gap-[2px] p-2 bg-white border-4 border-black rounded-lg shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"
        style={{ width: "128px", height: "128px" }}
      >
        {gridMatrix.map((row, rIdx) =>
          row.map((cell, cIdx) => {
            let bgClass = "bg-transparent";
            if (cell === 1) {
              // Border / theme color block
              return (
                <div 
                  key={`${rIdx}-${cIdx}`} 
                  style={{ backgroundColor: color }} 
                  className="rounded-[1px] transition-colors duration-200"
                />
              );
            }
            if (cell === 2) {
              bgClass = "bg-black"; // Eyes / mouth details
            }
            if (cell === 3) {
              bgClass = "bg-cyan-400 animate-pulse"; // Visor glow
            }
            return (
              <div 
                key={`${rIdx}-${cIdx}`} 
                className={`${bgClass} rounded-[1px]`} 
              />
            );
          })
        )}
      </div>

      {/* State Badge */}
      <div 
        className="absolute -bottom-2 px-3 py-1 bg-black text-white text-[10px] font-black uppercase rounded-md border-2 border-white shadow-[2px_2px_0px_0px_rgba(255,255,255,1)]"
      >
        {state}
      </div>
    </motion.div>
  );
};
