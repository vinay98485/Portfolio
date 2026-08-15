import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vinay kumar Mandalapu | AI/ML Engineer Portfolio",
  description:
    "Production AI Engineer Portfolio of Vinay kumar Mandalapu. Specializing in Machine Learning, Deep Learning, Computer Vision, and RAG Systems.",
  keywords: [
    "Vinay kumar Mandalapu",
    "AI/ML Engineer",
    "Python Developer",
    "Machine Learning Portfolio",
    "Deep Learning",
    "Computer Vision",
    "RAG Systems",
    "FastAPI",
    "Streamlit",
  ],
  authors: [{ name: "Vinay kumar Mandalapu" }],
  openGraph: {
    title: "Vinay kumar Mandalapu | AI/ML Engineer Portfolio",
    description:
      "Building practical AI systems using Machine Learning, Deep Learning, Generative AI, and RAG.",
    type: "website",
    locale: "en_US",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className="bg-[#080d1a] text-slate-100 antialiased selection:bg-cyan-500 selection:text-slate-950">
        {children}
      </body>
    </html>
  );
}
