"use client";

import React, { useState } from "react";
import { Navbar } from "../components/Navbar";
import { Hero } from "../components/Hero";
import { About } from "../components/About";
import { Skills } from "../components/Skills";
import { Projects } from "../components/Projects";
import { Timeline } from "../components/Timeline";
import { Education } from "../components/Education";
import { Certifications } from "../components/Certifications";
import { Contact } from "../components/Contact";
import { Footer } from "../components/Footer";
import { AIChatButton } from "../components/AIChatButton";
import { AIChatWindow } from "../components/AIChatWindow";

export default function Home() {
  const [aiWidgetOpen, setAiWidgetOpen] = useState(false);

  const handleOpenAI = () => setAiWidgetOpen(true);
  const handleToggleAI = () => setAiWidgetOpen((prev) => !prev);
  const handleCloseAI = () => setAiWidgetOpen(false);

  return (
    <main className="min-h-screen bg-[#080d1a] text-slate-100 relative selection:bg-cyan-500 selection:text-slate-950">
      {/* Sticky Header Navbar */}
      <Navbar onOpenAI={handleOpenAI} />

      {/* Hero Section */}
      <Hero onOpenAI={handleOpenAI} />

      {/* About Section */}
      <About />

      {/* Skills Section */}
      <Skills />

      {/* Projects Section */}
      <Projects />

      {/* Experience & Timeline Section */}
      <Timeline />

      {/* Education Section */}
      <Education />

      {/* Certifications Section */}
      <Certifications />

      {/* Contact Section */}
      <Contact onOpenAI={handleOpenAI} />

      {/* Footer */}
      <Footer />

      {/* Recruiter Floating AI Assistant Widget */}
      <AIChatButton onClick={handleToggleAI} isOpen={aiWidgetOpen} />
      <AIChatWindow isOpen={aiWidgetOpen} onClose={handleCloseAI} />
    </main>
  );
}
