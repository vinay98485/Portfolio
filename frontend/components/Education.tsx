"use client";

import React from "react";
import { motion } from "framer-motion";
import { GraduationCap, Award, Calendar, BookOpen } from "lucide-react";
import profileData from "../data/profile.json";

export const Education: React.FC = () => {
  return (
    <section id="education" className="py-20 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">ACADEMIC BACKGROUND</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Education & <span className="text-gradient">Academic Excellence</span>
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {profileData.education.map((edu, idx) => (
            <motion.div
              key={edu.degree}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: idx * 0.15 }}
              className="glass-card glass-card-hover p-8 rounded-3xl border border-slate-800/80 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-4 mb-6">
                  <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    <GraduationCap className="w-6 h-6" />
                  </div>
                  <span className="px-3 py-1 text-xs font-mono text-cyan-400 bg-slate-900/80 rounded-full border border-cyan-500/20 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{edu.period}</span>
                  </span>
                </div>

                <h4 className="text-xl font-bold text-slate-100 mb-2">{edu.degree}</h4>
                <p className="text-slate-400 text-sm font-medium mb-4 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-slate-500" />
                  <span>{edu.institution}</span>
                </p>
              </div>

              <div className="pt-4 border-t border-slate-800/80 flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-400" />
                <span className="text-sm font-semibold text-emerald-400 font-mono">{edu.score}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
