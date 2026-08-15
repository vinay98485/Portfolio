"use client";

import React from "react";
import Image from "next/image";
import { ExternalLink, AlertCircle, CheckCircle2, Layers } from "lucide-react";
import { GithubIcon } from "./Icons";

export interface Project {
  id: string;
  title: string;
  domain: string;
  image: string;
  description: string;
  problem: string;
  solution: string;
  technologies: string[];
  githubUrl: string;
  liveDemoUrl?: string | null;
  featured?: boolean;
}

interface ProjectCardProps {
  project: Project;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  return (
    <div className="glass-card glass-card-hover rounded-3xl border border-slate-800/80 overflow-hidden flex flex-col h-full bg-[#0b1120]/80">
      {/* Image Banner */}
      <div className="relative w-full h-52 sm:h-56 bg-slate-950 overflow-hidden border-b border-slate-800/80 group">
        <Image
          src={project.image}
          alt={project.title}
          fill
          className="object-cover object-center group-hover:scale-105 transition-transform duration-500"
        />
        {/* Top Badges Overlay */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-none">
          <span className="px-3 py-1 rounded-full text-[11px] font-mono font-semibold text-cyan-300 bg-slate-900/90 backdrop-blur-md border border-cyan-500/30">
            {project.domain}
          </span>
          {project.liveDemoUrl && (
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              LIVE DEMO
            </span>
          )}
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-[#0b1120] via-transparent to-transparent opacity-80" />
      </div>

      {/* Card Content */}
      <div className="p-6 flex-1 flex flex-col justify-between space-y-6">
        <div>
          {/* Title */}
          <h4 className="text-xl font-bold text-slate-100 tracking-tight mb-3 hover:text-cyan-400 transition-colors">
            {project.title}
          </h4>

          {/* Short Description */}
          <p className="text-slate-400 text-xs sm:text-sm leading-relaxed mb-4">
            {project.description}
          </p>

          {/* Problem & Solution Accordion-style layout */}
          <div className="space-y-3 pt-3 border-t border-slate-800/80">
            {/* Problem */}
            <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-800/60">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 mb-1">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Problem</span>
              </div>
              <p className="text-slate-300 text-xs leading-relaxed">{project.problem}</p>
            </div>

            {/* Solution */}
            <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-800/60">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-cyan-400 mb-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Solution & Architecture</span>
              </div>
              <p className="text-slate-300 text-xs leading-relaxed">{project.solution}</p>
            </div>
          </div>

          {/* Tech Stack */}
          <div className="mt-4">
            <div className="text-[11px] font-mono text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Layers className="w-3 h-3" />
              <span>Tech Stack:</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {project.technologies.map((tech) => (
                <span
                  key={tech}
                  className="px-2.5 py-0.5 text-[11px] font-medium text-slate-300 bg-slate-900 rounded-md border border-slate-800"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Buttons Action Bar */}
        <div className="flex items-center gap-3 pt-4 border-t border-slate-800/80">
          {/* GitHub Button */}
          <a
            href={project.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl glass-card hover:bg-slate-800 text-slate-200 hover:text-cyan-400 font-semibold text-xs transition-all border border-slate-700/80"
          >
            <GithubIcon className="w-4 h-4" />
            <span>GitHub Repo</span>
          </a>

          {/* Live Demo Button if available */}
          {project.liveDemoUrl && (
            <a
              href={project.liveDemoUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-cyan-500/20 transition-all"
            >
              <span>Live Demo</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
