"use client";

import React from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { Mail, FileText, Sparkles, ArrowRight, BrainCircuit } from "lucide-react";
import { GithubIcon, LinkedinIcon } from "./Icons";

interface HeroProps {
  onOpenAI: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onOpenAI }) => {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden bg-radial-glow">
      {/* Background Subtle Ambient Lights */}
      <div className="absolute top-1/4 left-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Text Content Column */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="lg:col-span-7 flex flex-col items-start"
          >
            {/* Status Tag */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass-card text-xs font-mono text-cyan-400 border border-cyan-500/20 mb-6">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>OPEN TO WORK — AI/ML ENGINEER</span>
            </div>

            {/* Main Name Heading */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white mb-4">
              Hi, I&apos;m <span className="text-gradient">Vinay kumar</span> Mandalapu
            </h1>

            {/* Subtitle Role */}
            <h2 className="text-xl sm:text-2xl font-semibold text-slate-300 mb-6 flex items-center gap-2">
              <BrainCircuit className="w-6 h-6 text-cyan-400 shrink-0" />
              <span>AI/ML Engineer | Python Developer</span>
            </h2>

            {/* Statement */}
            <p className="text-slate-400 text-base sm:text-lg leading-relaxed max-w-2xl mb-8">
              Building practical AI systems using Machine Learning, Deep Learning, Generative AI and RAG.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4 w-full sm:w-auto mb-10">
              <a
                href="#projects"
                className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/25 transition-all hover:scale-[1.02] active:scale-[0.98] w-full sm:w-auto"
              >
                <span>View Projects</span>
                <ArrowRight className="w-4 h-4" />
              </a>

              <a
                href="/resume.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl glass-card hover:bg-slate-800/80 text-slate-200 hover:text-cyan-400 font-semibold text-sm transition-all border border-slate-700/80 w-full sm:w-auto"
              >
                <FileText className="w-4 h-4" />
                <span>Download Resume</span>
              </a>

              <button
                onClick={onOpenAI}
                className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-cyan-300 font-semibold text-sm border border-cyan-500/40 shadow-lg shadow-cyan-900/20 transition-all hover:scale-[1.02] active:scale-[0.98] w-full sm:w-auto cursor-pointer"
              >
                <Sparkles className="w-4 h-4 fill-cyan-400 text-cyan-400" />
                <span>Ask AI About Me</span>
              </button>
            </div>

            {/* Social Icons */}
            <div className="flex items-center gap-4 pt-4 border-t border-slate-800/80 w-full">
              <span className="text-xs font-mono text-slate-500 uppercase tracking-wider">Connect:</span>
              <a
                href="https://github.com/vinay98485/"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-lg glass-card text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
                aria-label="GitHub Profile"
              >
                <GithubIcon className="w-5 h-5" />
              </a>
              <a
                href="https://www.linkedin.com/in/vinay-kumar-mandalapu"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-lg glass-card text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
                aria-label="LinkedIn Profile"
              >
                <LinkedinIcon className="w-5 h-5" />
              </a>
              <a
                href="mailto:vinaykumar98485@gmail.com"
                className="p-2.5 rounded-lg glass-card text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition-colors"
                aria-label="Email Contact"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </motion.div>

          {/* Profile Image Column */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="lg:col-span-5 flex justify-center"
          >
            <div className="relative w-72 h-72 sm:w-80 sm:h-80 lg:w-96 lg:h-96">
              {/* Outer Glowing Ring */}
              <div className="absolute -inset-1 rounded-3xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-500 opacity-40 blur-xl animate-pulse" />

              {/* Card Container */}
              <div className="relative w-full h-full rounded-3xl p-2 glass-card border border-cyan-500/30 overflow-hidden shadow-2xl">
                <div className="relative w-full h-full rounded-2xl overflow-hidden bg-slate-950">
                  <Image
                    src="/profile.jpg"
                    alt="Vinay kumar Mandalapu"
                    fill
                    priority
                    className="object-cover object-top hover:scale-105 transition-transform duration-500"
                  />
                  {/* Overlay Gradient */}
                  <div className="absolute inset-0 bg-gradient-to-t from-[#080d1a] via-transparent to-transparent opacity-40" />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
