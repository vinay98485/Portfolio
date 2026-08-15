"use client";

import React, { useState, useEffect } from "react";
import { Bot, Sparkles, Menu, X, ArrowUpRight } from "lucide-react";

interface NavbarProps {
  onOpenAI: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenAI }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { name: "About", href: "#about" },
    { name: "Skills", href: "#skills" },
    { name: "Projects", href: "#projects" },
    { name: "Experience", href: "#experience" },
    { name: "Education", href: "#education" },
    { name: "Contact", href: "#contact" },
  ];

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        scrolled
          ? "bg-[#080d1a]/85 backdrop-blur-md border-b border-slate-800/80 py-3 shadow-xl shadow-black/20"
          : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        {/* Brand */}
        <a href="#" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-[#0b1120] rounded-[10px] flex items-center justify-center">
              <span className="font-bold text-cyan-400 text-base tracking-wider leading-none">VK</span>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-slate-100 tracking-tight text-base group-hover:text-cyan-400 transition-colors">
              Vinay kumar M.
            </span>
            <span className="text-[11px] text-cyan-400 font-mono tracking-wider">
              AI/ML ENGINEER
            </span>
          </div>
        </a>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-full border border-slate-800/80 backdrop-blur-md">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              className="px-4 py-1.5 text-xs font-medium text-slate-300 hover:text-cyan-400 hover:bg-slate-800/60 rounded-full transition-all"
            >
              {link.name}
            </a>
          ))}
        </nav>

        {/* Actions */}
        <div className="hidden sm:flex items-center gap-3">
          <button
            onClick={onOpenAI}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-slate-900 bg-gradient-to-r from-cyan-400 to-indigo-400 hover:from-cyan-300 hover:to-indigo-300 rounded-full shadow-lg shadow-cyan-500/20 transition-all hover:scale-105 active:scale-95 cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 fill-slate-900" />
            <span>Ask AI Assistant</span>
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-slate-300 hover:text-cyan-400 focus:outline-none"
          aria-label="Toggle Menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Nav Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#0b1120]/95 backdrop-blur-xl border-b border-slate-800 px-4 pt-3 pb-6 space-y-3">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 text-sm font-medium text-slate-200 hover:text-cyan-400 hover:bg-slate-800/50 rounded-lg"
            >
              {link.name}
            </a>
          ))}
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenAI();
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-semibold text-slate-900 bg-gradient-to-r from-cyan-400 to-indigo-400 rounded-lg shadow-lg"
          >
            <Sparkles className="w-4 h-4 fill-slate-900" />
            <span>Ask AI Assistant</span>
          </button>
        </div>
      )}
    </header>
  );
};
