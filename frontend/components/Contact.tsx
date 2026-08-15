"use client";

import React from "react";
import { motion } from "framer-motion";
import { Mail, Phone, MapPin, Send, Sparkles } from "lucide-react";
import { GithubIcon, LinkedinIcon } from "./Icons";

interface ContactProps {
  onOpenAI: () => void;
}

export const Contact: React.FC<ContactProps> = ({ onOpenAI }) => {
  return (
    <section id="contact" className="py-20 relative bg-slate-950/60 border-t border-slate-800/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">GET IN TOUCH</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-4">
            Let&apos;s Build <span className="text-gradient">Together</span>
          </h3>
          <p className="text-slate-400 text-sm sm:text-base">
            Open to full-time AI/ML Engineering roles, collaborative research, and software engineering opportunities.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-5xl mx-auto">
          {/* Direct Contact Info Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-6 glass-card p-8 rounded-3xl border border-slate-800/80 space-y-6"
          >
            <h4 className="text-xl font-bold text-slate-100 mb-6">Contact Information</h4>

            <div className="space-y-4">
              <a
                href="mailto:vinaykumar98485@gmail.com"
                className="flex items-center gap-4 p-4 rounded-2xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 text-slate-200 hover:text-cyan-400 transition-all group"
              >
                <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 group-hover:scale-110 transition-transform">
                  <Mail className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-xs text-slate-500 block font-mono">EMAIL ADDRESS</span>
                  <span className="text-sm font-semibold">vinaykumar98485@gmail.com</span>
                </div>
              </a>

              <a
                href="tel:+916304209763"
                className="flex items-center gap-4 p-4 rounded-2xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 text-slate-200 hover:text-cyan-400 transition-all group"
              >
                <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 group-hover:scale-110 transition-transform">
                  <Phone className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-xs text-slate-500 block font-mono">PHONE NUMBER</span>
                  <span className="text-sm font-semibold">+91 6304209763</span>
                </div>
              </a>

              <div className="flex items-center gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-slate-200">
                <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  <MapPin className="w-5 h-5" />
                </div>
                <div>
                  <span className="text-xs text-slate-500 block font-mono">LOCATION</span>
                  <span className="text-sm font-semibold">Hyderabad, Telangana, India</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Social & AI Assistant Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="lg:col-span-6 glass-card p-8 rounded-3xl border border-slate-800/80 flex flex-col justify-between"
          >
            <div>
              <h4 className="text-xl font-bold text-slate-100 mb-4">Professional Profiles</h4>
              <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                Connect with me on GitHub to explore open-source repository pipelines or visit my LinkedIn profile for technical updates.
              </p>

              <div className="grid grid-cols-2 gap-4 mb-8">
                <a
                  href="https://github.com/vinay98485/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 rounded-2xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-200 hover:text-cyan-400 transition-all font-semibold text-sm"
                >
                  <GithubIcon className="w-5 h-5 text-cyan-400" />
                  <span>GitHub</span>
                </a>

                <a
                  href="https://www.linkedin.com/in/vinay-kumar-mandalapu"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 rounded-2xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-slate-200 hover:text-cyan-400 transition-all font-semibold text-sm"
                >
                  <LinkedinIcon className="w-5 h-5 text-cyan-400" />
                  <span>LinkedIn</span>
                </a>
              </div>
            </div>

            {/* AI Callout */}
            <div className="p-5 rounded-2xl bg-gradient-to-r from-cyan-950/60 to-indigo-950/60 border border-cyan-500/30 flex items-center justify-between">
              <div>
                <h5 className="text-sm font-bold text-white flex items-center gap-1.5 mb-1">
                  <Sparkles className="w-4 h-4 text-cyan-400 fill-cyan-400" />
                  <span>Have questions for Vinay?</span>
                </h5>
                <p className="text-xs text-slate-400">Ask my interactive RAG AI Assistant instant questions.</p>
              </div>
              <button
                onClick={onOpenAI}
                className="px-4 py-2 text-xs font-bold text-slate-950 bg-cyan-400 hover:bg-cyan-300 rounded-xl transition-all cursor-pointer shadow-md shadow-cyan-500/20 shrink-0"
              >
                Ask AI
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
