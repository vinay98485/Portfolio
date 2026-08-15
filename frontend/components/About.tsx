"use client";

import React from "react";
import { motion } from "framer-motion";
import { Cpu, Terminal, Layers, Database, ShieldCheck, Zap } from "lucide-react";

export const About: React.FC = () => {
  const highlights = [
    {
      icon: Terminal,
      title: "Hands-On Engineering",
      description: "Driven by practical project execution, translating theoretical Machine Learning and Deep Learning concepts into deployed applications.",
    },
    {
      icon: Cpu,
      title: "Deep Learning & Vision",
      description: "Experience engineering CNNs for multiclass image classification (99.01% test accuracy) and ANNs for customer churn prediction.",
    },
    {
      icon: Database,
      title: "Customer & Risk Analytics",
      description: "Architected multi-phase ML systems for RFM customer segmentation, churn probability forecasting, and XGBoost credit risk scoring APIs.",
    },
    {
      icon: ShieldCheck,
      title: "Secure Full-Stack Systems",
      description: "Built web engines with Django, FastAPI, and Streamlit, incorporating AES-256 CTR encryption and PBKDF2 security.",
    },
  ];

  return (
    <section id="about" className="py-20 relative bg-slate-950/50 border-y border-slate-800/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">ENGINEERING PROFILE</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Building Real-World <span className="text-gradient">Artificial Intelligence Systems</span>
          </h3>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Main Narrative Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-6 glass-card p-8 rounded-3xl border border-slate-800/80 space-y-5"
          >
            <h4 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              <span>Engineering Journey</span>
            </h4>
            
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Programming began as an academic curriculum requirement, but quickly transformed into an engineering focus when building software to solve real-world analytical problems.
            </p>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              My technical work centers on predictive analytics, computer vision, financial modeling, and Generative AI. I have developed a <strong className="text-cyan-400 font-semibold">Bitcoin Price Prediction system</strong> using Subspace Learning (SPCE) and ARIMA/Linear Regression, a <strong className="text-cyan-400 font-semibold">Fruit Freshness Classifier</strong> using TensorFlow/CNNs, an <strong className="text-cyan-400 font-semibold">Enterprise E-Commerce AI Retention Engine</strong> combining RFM segmentation with XGBoost, and an <strong className="text-cyan-400 font-semibold">End-to-End Credit Risk Scoring Engine</strong>.
            </p>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Currently completing a Bachelor of Technology in Computer Science (Computational Science) at Siddhartha Institute of Engineering & Technology (CGPA: 8.3/10), my focus is expanding production expertise in AI Engineering, Retrieval-Augmented Generation (RAG), and scalable ML backend APIs.
            </p>
          </motion.div>

          {/* Grid of Highlight Cards */}
          <div className="lg:col-span-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {highlights.map((item, index) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className="glass-card glass-card-hover p-6 rounded-2xl border border-slate-800/80 flex flex-col items-start"
              >
                <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 mb-4 border border-cyan-500/20">
                  <item.icon className="w-6 h-6" />
                </div>
                <h5 className="text-base font-bold text-slate-100 mb-2">{item.title}</h5>
                <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
