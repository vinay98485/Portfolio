"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, X, RotateCcw, Sparkles, User, CheckCircle2 } from "lucide-react";
import { QuestionMenu } from "./QuestionMenu";
import { ChatMessage } from "./ChatMessage";

interface AIChatWindowProps {
  isOpen: boolean;
  onClose: () => void;
}

interface QAState {
  question: string;
  answer: string;
  cached?: boolean;
}

export const AIChatWindow: React.FC<AIChatWindowProps> = ({ isOpen, onClose }) => {
  const [selectedQuestion, setSelectedQuestion] = useState<string | null>(null);
  const [selectedQA, setSelectedQA] = useState<QAState | null>(null);
  const [loading, setLoading] = useState(false);

  const RAG_API_URL = process.env.NEXT_PUBLIC_RAG_API_URL || "https://vinay-portfolio-rag.onrender.com";

  const handleSelectQuestion = async (question: string) => {
    // Show user question immediately for fast feedback
    setSelectedQuestion(question);
    setLoading(true);
    setSelectedQA(null);

    try {
      const res = await fetch(`${RAG_API_URL.replace(/\/$/, "")}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      setSelectedQA({
        question,
        answer: data.answer || "No response received.",
        cached: data.cached || false,
      });
    } catch (err: any) {
      console.error("RAG API Fetch Error:", err);
      // Fast fallback response if network API takes long or fails
      setSelectedQA({
        question,
        answer: getFallbackAnswer(question),
        cached: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const getFallbackAnswer = (q: string): string => {
    const lower = q.toLowerCase();
    if (lower.includes("project")) {
      return "Vinay has built several high-impact AI projects including Bank Customer Churn Prediction (ANN), Fruit Freshness Classifier (CNN - 99.01% accuracy), Enterprise E-Commerce AI Retention Engine (RFM + XGBoost), Credit Risk Scoring Engine (XGBoost REST API), Customer Segmentation (K-Means), and Bitcoin Price Prediction (SPCE + ARIMA).";
    }
    if (lower.includes("technology") || lower.includes("skill")) {
      return "Vinay's technical stack includes Python, Java, SQL, Scikit-Learn, TensorFlow, Keras, OpenCV, XGBoost, FastAPI, Django, Streamlit, Docker, Git, ChromaDB, and Retrieval-Augmented Generation (RAG).";
    }
    if (lower.includes("hire") || lower.includes("experience") || lower.includes("background")) {
      return "Vinay kumar Mandalapu is a Computer Science Engineering student at Siddhartha Institute of Engineering & Technology (CGPA: 8.3/10). He specializes in translating theoretical AI/ML into practical production applications with clean architecture and proven metrics.";
    }
    return "Vinay is an AI/ML Engineer and Python Developer specializing in Machine Learning, Deep Learning, Computer Vision, and RAG architectures.";
  };

  const handleReset = () => {
    setSelectedQuestion(null);
    setSelectedQA(null);
    setLoading(false);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 15, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 15, scale: 0.96 }}
          transition={{ duration: 0.15, ease: "easeOut" }}
          className="fixed bottom-24 right-4 sm:right-6 z-50 w-[92vw] sm:w-[420px] max-h-[85vh] glass-card rounded-3xl border border-slate-700/80 shadow-2xl shadow-black/60 overflow-hidden flex flex-col bg-[#0b1120]/95 backdrop-blur-xl"
        >
          {/* Header */}
          <div className="p-4 sm:p-5 bg-gradient-to-r from-[#0d1527] to-[#131b2e] border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-cyan-400 to-indigo-500 flex items-center justify-center text-slate-950 font-bold shadow-md shadow-cyan-500/20">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-white text-base leading-tight flex items-center gap-1.5">
                  <span>Ask Vinay AI</span>
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400" />
                </h3>
                <span className="text-[10px] font-mono text-cyan-400 tracking-wider">
                  RAG PORTFOLIO ASSISTANT
                </span>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors cursor-pointer"
              aria-label="Close AI Widget"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body Content */}
          <div className="p-4 sm:p-5 flex-1 overflow-y-auto overflow-x-hidden space-y-4 min-h-[320px] min-w-0 w-full">
            {selectedQuestion && loading ? (
              <div className="space-y-4 text-xs sm:text-sm">
                {/* Instant User Question Bubble */}
                <div className="flex items-start justify-end gap-2">
                  <div className="p-3.5 rounded-2xl rounded-tr-none bg-gradient-to-r from-cyan-500 to-indigo-600 text-white max-w-[85%] shadow-md">
                    <p className="font-medium leading-relaxed">{selectedQuestion}</p>
                  </div>
                  <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                    <User className="w-4 h-4" />
                  </div>
                </div>

                {/* AI Thinking Bubble */}
                <div className="flex items-start gap-2">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-cyan-400 to-indigo-500 flex items-center justify-center text-slate-950 font-bold shrink-0 mt-1 shadow-md shadow-cyan-500/20">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="p-4 rounded-2xl rounded-tl-none glass-card border border-slate-800 text-slate-300 max-w-[88%] flex items-center gap-2">
                    <span className="text-xs font-mono text-cyan-400">AI is analyzing knowledge base</span>
                    <span className="flex gap-1 items-center ml-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                    </span>
                  </div>
                </div>
              </div>
            ) : selectedQA ? (
              <div className="space-y-6">
                <ChatMessage
                  question={selectedQA.question}
                  answer={selectedQA.answer}
                  cached={selectedQA.cached}
                />

                {/* Ask Another Question Button */}
                <div className="pt-2 flex justify-center">
                  <button
                    onClick={handleReset}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-cyan-400 hover:text-cyan-300 font-semibold text-xs transition-all cursor-pointer shadow-lg hover:scale-105 active:scale-95"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Ask Another Question</span>
                  </button>
                </div>
              </div>
            ) : (
              <QuestionMenu onSelectQuestion={handleSelectQuestion} />
            )}
          </div>

          {/* Footer Info */}
          <div className="p-3 bg-slate-950/80 border-t border-slate-800/80 text-center">
            <span className="text-[10px] font-mono text-slate-500">
              Powered by Gemini Embeddings + ChromaDB Vector RAG
            </span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
