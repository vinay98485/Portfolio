"use client";

import React from "react";
import { MessageSquare, HelpCircle } from "lucide-react";
import questionsData from "../data/questions.json";

export interface QuestionItem {
  id: number;
  question: string;
}

interface QuestionMenuProps {
  onSelectQuestion: (question: string) => void;
}

export const QuestionMenu: React.FC<QuestionMenuProps> = ({ onSelectQuestion }) => {
  const questions: QuestionItem[] = questionsData as QuestionItem[];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-2">
        <HelpCircle className="w-4 h-4 text-cyan-400" />
        <span>Select a question to learn more about Vinay:</span>
      </div>

      <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
        {questions.map((q) => (
          <button
            key={q.id}
            onClick={() => onSelectQuestion(q.question)}
            className="w-full text-left p-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/40 text-slate-200 hover:text-cyan-300 text-xs font-medium transition-all flex items-start gap-2.5 group cursor-pointer"
          >
            <MessageSquare className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 shrink-0 mt-0.5" />
            <span className="leading-snug">{q.question}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
