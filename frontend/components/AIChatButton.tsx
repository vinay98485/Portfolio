"use client";

import React from "react";
import { Bot, Sparkles } from "lucide-react";

interface AIChatButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export const AIChatButton: React.FC<AIChatButtonProps> = ({ onClick, isOpen }) => {
  return (
    <button
      onClick={onClick}
      className={`fixed bottom-6 right-6 z-50 p-4 rounded-full shadow-2xl transition-all duration-300 flex items-center justify-center group cursor-pointer ${
        isOpen
          ? "bg-slate-800 text-slate-400 rotate-90 border border-slate-700"
          : "bg-gradient-to-r from-cyan-400 via-indigo-500 to-purple-500 text-slate-950 hover:scale-110 shadow-cyan-500/30"
      }`}
      aria-label="Toggle AI Portfolio Assistant"
    >
      {!isOpen && (
        <span className="absolute -inset-1 rounded-full bg-gradient-to-r from-cyan-400 to-indigo-500 opacity-75 blur-md group-hover:opacity-100 transition-opacity animate-pulse" />
      )}

      <div className="relative flex items-center justify-center">
        <Bot className={`w-7 h-7 ${isOpen ? "text-slate-300" : "text-slate-950 font-bold"}`} />
        {!isOpen && (
          <Sparkles className="w-3.5 h-3.5 text-cyan-200 absolute -top-1 -right-1 fill-cyan-200 animate-bounce" />
        )}
      </div>
    </button>
  );
};
