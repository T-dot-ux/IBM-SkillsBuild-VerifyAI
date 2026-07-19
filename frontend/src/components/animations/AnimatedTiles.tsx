"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function AnimatedTiles() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  // Generate 20 random tiles that float across the screen
  const tiles = Array.from({ length: 20 }).map((_, i) => ({
    id: i,
    size: Math.random() * 40 + 10,
    xStart: Math.random() * 100,
    yStart: Math.random() * 100,
    delay: Math.random() * 5,
    duration: Math.random() * 10 + 10,
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
      {tiles.map((tile) => (
        <motion.div
          key={tile.id}
          className="absolute bg-cyan-500/10 border border-cyan-400/20 rounded-md backdrop-blur-sm"
          style={{
            width: tile.size,
            height: tile.size,
            left: `${tile.xStart}%`,
            top: `${tile.yStart}%`,
          }}
          animate={{
            x: [0, Math.random() * 200 - 100, Math.random() * 400 - 200],
            y: [0, Math.random() * -200 - 50, Math.random() * -400 - 100],
            rotate: [0, 90, 180, 360],
            opacity: [0, 0.6, 0],
            scale: [0.5, 1.2, 0.5],
          }}
          transition={{
            duration: tile.duration,
            delay: tile.delay,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      ))}
    </div>
  );
}
