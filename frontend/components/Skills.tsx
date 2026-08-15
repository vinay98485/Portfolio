"use client";

import React from "react";
import { motion } from "framer-motion";
import { Code, Brain, Cpu, Sparkles, Server, Wrench } from "lucide-react";

export const Skills: React.FC = () => {
  const skillCategories = [
    {
      title: "Programming",
      icon: Code,
      color: "from-blue-500/20 to-cyan-500/20",
      borderColor: "border-blue-500/30",
      iconColor: "text-blue-400",
      skills: ["Python", "Java", "C", "SQL (MySQL)"],
    },
    {
      title: "Machine Learning",
      icon: Brain,
      color: "from-indigo-500/20 to-purple-500/20",
      borderColor: "border-indigo-500/30",
      iconColor: "text-indigo-400",
      skills: [
        "Scikit-Learn",
        "Feature Engineering",
        "Model Evaluation",
        "Logistic Regression",
        "Linear Regression",
        "SVM",
        "ARIMA",
        "SPCE Subspace Learning",
        "XGBoost",
        "K-Means",
      ],
    },
    {
      title: "Deep Learning",
      icon: Cpu,
      color: "from-cyan-500/20 to-emerald-500/20",
      borderColor: "border-cyan-500/30",
      iconColor: "text-cyan-400",
      skills: ["TensorFlow", "Keras", "ANN (Neural Networks)", "CNN (Convolutional Networks)", "EarlyStopping", "Batch Normalization"],
    },
    {
      title: "Generative AI",
      icon: Sparkles,
      color: "from-purple-500/20 to-pink-500/20",
      borderColor: "border-purple-500/30",
      iconColor: "text-purple-400",
      skills: ["RAG (Retrieval-Augmented Generation)", "Gemini API", "Claude 101", "Vector DBs (ChromaDB)", "GitHub Copilot"],
    },
    {
      title: "Backend & Web",
      icon: Server,
      color: "from-emerald-500/20 to-teal-500/20",
      borderColor: "border-emerald-500/30",
      iconColor: "text-emerald-400",
      skills: ["FastAPI", "Django", "REST APIs", "Streamlit", "MySQL"],
    },
    {
      title: "Tools & OS",
      icon: Wrench,
      color: "from-amber-500/20 to-orange-500/20",
      borderColor: "border-amber-500/30",
      iconColor: "text-amber-400",
      skills: ["Docker", "Git", "GitHub", "Linux", "Windows"],
    },
  ];

  return (
    <section id="skills" className="py-20 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">TECHNICAL STACK</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Specialized Skills & <span className="text-gradient">Core Competencies</span>
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {skillCategories.map((category, idx) => (
            <motion.div
              key={category.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: idx * 0.1 }}
              className={`glass-card glass-card-hover p-6 rounded-2xl border ${category.borderColor} bg-gradient-to-br ${category.color} flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className={`p-2.5 rounded-xl bg-slate-900/80 ${category.iconColor} border border-slate-800`}>
                    <category.icon className="w-5 h-5" />
                  </div>
                  <h4 className="text-lg font-bold text-slate-100">{category.title}</h4>
                </div>

                <div className="flex flex-wrap gap-2 mt-4">
                  {category.skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-3 py-1 text-xs font-medium text-slate-300 bg-slate-900/70 rounded-lg border border-slate-800/80 hover:border-cyan-500/30 hover:text-cyan-300 transition-colors"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
