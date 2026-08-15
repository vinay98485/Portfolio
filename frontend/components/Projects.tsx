"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { ProjectCard, Project } from "./ProjectCard";
import projectsData from "../data/projects.json";

export const Projects: React.FC = () => {
  const [filter, setFilter] = useState<string>("All");

  const categories = ["All", "Deep Learning", "Machine Learning", "Computer Vision", "Financial ML"];

  const projects: Project[] = projectsData as Project[];

  const filteredProjects =
    filter === "All"
      ? projects
      : projects.filter((p) => p.domain.toLowerCase().includes(filter.toLowerCase()));

  return (
    <section id="projects" className="py-20 relative bg-slate-950/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-xs font-mono text-cyan-400 uppercase tracking-widest mb-2">PORTFOLIO PROJECTS</h2>
          <h3 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mb-4">
            Featured <span className="text-gradient">AI & Engineering Systems</span>
          </h3>
          <p className="text-slate-400 text-sm sm:text-base">
            Verified production-style machine learning, deep learning, computer vision, and full-stack API projects.
          </p>
        </div>

        {/* Filter Badges */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-12">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-4 py-2 text-xs font-semibold rounded-full transition-all cursor-pointer ${
                filter === cat
                  ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20"
                  : "glass-card text-slate-400 hover:text-cyan-400 hover:bg-slate-800"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredProjects.map((project, idx) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.1 }}
              className="h-full"
            >
              <ProjectCard project={project} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
