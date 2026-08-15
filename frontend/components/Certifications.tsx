"use client";

import React from "react";
import { motion } from "framer-motion";
import { Award, CheckCircle, ShieldCheck } from "lucide-react";
import profileData from "../data/profile.json";

export const Certifications: React.FC = () => {
  return (
    <section className="py-20 relative bg-slate-950/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">VERIFIED CREDENTIALS</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Industry <span className="text-gradient">Certifications & Training</span>
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {profileData.certifications.map((cert, idx) => (
            <motion.div
              key={cert.name}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
              className="glass-card glass-card-hover p-6 rounded-2xl border border-slate-800/80 flex items-start gap-4"
            >
              <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0">
                <ShieldCheck className="w-6 h-6" />
              </div>

              <div>
                <h4 className="text-base font-bold text-slate-100 mb-1">{cert.name}</h4>
                <p className="text-xs font-mono text-cyan-400 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-cyan-400" />
                  <span>{cert.issuer}</span>
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
