"use client";

import React from "react";
import { Bot, User, CheckCircle2 } from "lucide-react";

interface ChatMessageProps {
  question: string;
  answer: string;
  cached?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ question, answer, cached }) => {
  // Strip out raw inline source annotations like *(Source: projects/abc.md)* or (Source: xyz.md)
  const cleanAnswer = (answer || "")
    .replace(/\*?\(Source:.*?\)\*?/gi, "")
    .replace(/\*?Source:.*?\*?/gi, "")
    .trim();

  // Parse inline markdown formatting like **bold** and `code`
  const parseInlineMarkdown = (str: string) => {
    const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);

    return parts.map((part, idx) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={idx} className="font-semibold text-cyan-300">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code key={idx} className="px-1.5 py-0.5 text-xs font-mono text-cyan-400 bg-slate-900 rounded border border-slate-800 break-all">
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  // Render paragraphs and list items cleanly
  const renderFormattedText = (text: string) => {
    if (!text) return null;
    const paragraphs = text.split(/\n\n+/);

    return paragraphs.map((para, pIdx) => {
      const lines = para.split("\n");

      return (
        <div key={pIdx} className="space-y-1.5 min-w-0">
          {lines.map((line, lIdx) => {
            const trimmed = line.trim();
            if (!trimmed) return null;

            if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
              const content = trimmed.substring(2);
              return (
                <div key={lIdx} className="flex items-start gap-2 pl-2 my-1 min-w-0">
                  <span className="text-cyan-400 font-bold shrink-0">•</span>
                  <span className="leading-relaxed break-words [overflow-wrap:anywhere] min-w-0">
                    {parseInlineMarkdown(content)}
                  </span>
                </div>
              );
            }

            return (
              <p key={lIdx} className="leading-relaxed break-words [overflow-wrap:anywhere] min-w-0">
                {parseInlineMarkdown(line)}
              </p>
            );
          })}
        </div>
      );
    });
  };

  return (
    <div className="space-y-4 text-xs sm:text-sm w-full min-w-0 overflow-hidden">
      {/* User Question Bubble */}
      <div className="flex items-start justify-end gap-2 w-full min-w-0">
        <div className="p-3.5 rounded-2xl rounded-tr-none bg-gradient-to-r from-cyan-500 to-indigo-600 text-white max-w-[85%] shadow-md break-words [overflow-wrap:anywhere]">
          <p className="font-medium leading-relaxed">{question}</p>
        </div>
        <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
          <User className="w-4 h-4" />
        </div>
      </div>

      {/* AI Answer Bubble */}
      <div className="flex items-start gap-2 w-full min-w-0">
        <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-cyan-400 to-indigo-500 flex items-center justify-center text-slate-950 font-bold shrink-0 mt-1 shadow-md shadow-cyan-500/20">
          <Bot className="w-4 h-4" />
        </div>
        <div className="p-4 rounded-2xl rounded-tl-none glass-card border border-slate-800 text-slate-200 flex-1 min-w-0 space-y-3 break-words [overflow-wrap:anywhere]">
          <div className="flex items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
            <span className="font-bold text-cyan-400 text-xs flex items-center gap-1">
              <span>Vinay Portfolio AI</span>
            </span>
            {cached && (
              <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1 shrink-0">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span>Verified Response</span>
              </span>
            )}
          </div>

          {/* Formatted Text Content */}
          <div className="text-slate-300 space-y-2 min-w-0 break-words [overflow-wrap:anywhere]">
            {renderFormattedText(cleanAnswer)}
          </div>
        </div>
      </div>
    </div>
  );
};
