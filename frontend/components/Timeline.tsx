"use client";

import React from "react";
import { motion } from "framer-motion";
import { Briefcase, CheckCircle2, Code2 } from "lucide-react";

export const Timeline: React.FC = () => {
  const experiences = [
    {
      role: "AI/ML Project Engineer & Developer",
      period: "2023 – Present",
      type: "Practical Project Development",
      description: "Designed, trained, and deployed end-to-end Machine Learning, Deep Learning, Computer Vision, and RAG systems.",
      highlights: [
        "Built Enterprise E-Commerce AI Retention Engine processing 540K+ retail transactions.",
        "Developed Fruit Freshness Computer Vision Classifier achieving 99.01% test accuracy.",
        "Engineered Bank Customer Churn Prediction ANN with Streamlit live forecasting.",
        "Architected Credit Risk Scoring XGBoost REST API in Django with Joblib model serialization.",
        "Created RAG Portfolio Assistant API powered by Gemini Embedding API and ChromaDB.",
      ],
    },
    {
      role: "Full-Stack Python Application Developer",
      period: "2022 – 2023",
      type: "Academic & Project Track",
      description: "Built full-stack Python web applications, custom algorithms, and database-driven solutions.",
      highlights: [
        "Created Resume Builder System in Django & MySQL with AES-256 CTR encryption & PBKDF2.",
        "Built Bitcoin Price Prediction system using Subspace Learning (SPCE) and Web3 blockchain smart contracts.",
        "Implemented K-Means Customer Segmentation dashboards with mathematical Elbow Method validation.",
      ],
    },
  ];

  return (
    <section id="experience" className="py-20 relative bg-slate-950/50 border-y border-slate-800/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">PRACTICAL TIMELINE</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Engineering <span className="text-gradient">Experience & Milestones</span>
          </h3>
        </div>

        <div className="max-w-4xl mx-auto relative border-l-2 border-slate-800 pl-6 sm:pl-8 space-y-12 ml-4 sm:ml-auto">
          {experiences.map((exp, idx) => (
            <motion.div
              key={exp.role}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.15 }}
              className="relative"
            >
              {/* Timeline Icon Node */}
              <div className="absolute -left-[35px] sm:-left-[43px] top-0.5 w-9 h-9 rounded-full bg-slate-900 border-2 border-cyan-500 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/20">
                <Briefcase className="w-4 h-4" />
              </div>

              <div className="glass-card p-6 sm:p-8 rounded-3xl border border-slate-800/80 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
                  <div>
                    <h4 className="text-xl font-bold text-slate-100">{exp.role}</h4>
                    <span className="text-xs font-mono text-cyan-400">{exp.type}</span>
                  </div>
                  <span className="px-3 py-1 text-xs font-mono text-slate-300 bg-slate-900 rounded-full border border-slate-800">
                    {exp.period}
                  </span>
                </div>

                <p className="text-slate-300 text-sm leading-relaxed">{exp.description}</p>

                <ul className="space-y-2 pt-2">
                  {exp.highlights.map((h, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs sm:text-sm text-slate-400">
                      <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
