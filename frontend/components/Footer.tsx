"use client";

import React from "react";
import { BrainCircuit, Heart } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="py-8 bg-[#050811] border-t border-slate-800/80 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-cyan-400" />
          <span className="font-semibold text-slate-300">Vinay kumar Mandalapu</span>
          <span>— AI/ML Engineer Portfolio</span>
        </div>

        <div className="flex items-center gap-1 text-slate-400">
          <span>Designed for recruiters & built with</span>
          <span className="text-cyan-400 font-mono">Next.js & Tailwind</span>
        </div>
      </div>
    </footer>
  );
};
