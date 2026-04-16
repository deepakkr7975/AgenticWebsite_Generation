"use client";
import Link from "next/link";

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-16 overflow-hidden"
      style={{ background: "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124,58,237,0.3) 0%, transparent 60%), #09090B" }}>
      <div className="absolute inset-0 opacity-[0.03]"
        style={{ backgroundImage: "linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)", backgroundSize: "64px 64px" }}/>
      <div className="relative z-10 mb-6 flex items-center gap-2 px-4 py-1.5 rounded-full border border-violet-500/30 bg-violet-500/10 backdrop-blur-sm animate-fade-in-up">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        <span className="text-xs font-medium text-violet-300">Now in public beta · No credit card needed</span>
      </div>
      <h1 className="relative z-10 text-center font-black leading-[1.05] tracking-tight text-5xl sm:text-6xl md:text-7xl lg:text-8xl max-w-5xl animate-fade-in-up [animation-delay:100ms]"
          style={{ fontFamily: "'Clash Display', sans-serif" }}>
        Ship features{" "}
        <span className="relative inline-block" style={{ background: "linear-gradient(135deg,#7C3AED 0%,#A78BFA 50%,#F59E0B 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
          10× faster
        </span>
        <br />with your team
      </h1>
      <p className="relative z-10 mt-6 max-w-2xl text-center text-lg sm:text-xl text-zinc-400 leading-relaxed animate-fade-in-up [animation-delay:200ms]">
        FlowForge is the project management platform built for developers and designers who refuse to slow down.
        Tasks, sprints, docs — all in one place.
      </p>
      <div className="relative z-10 mt-10 flex flex-col sm:flex-row gap-4 animate-fade-in-up [animation-delay:300ms]">
        <Link href="/signup" className="group inline-flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 shadow-lg shadow-violet-900/50 hover:shadow-violet-800/60 hover:-translate-y-0.5">
          Start for free
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 group-hover:translate-x-1 transition-transform">
            <path fillRule="evenodd" d="M3 10a.75.75 0 0 1 .75-.75h10.638L10.23 5.29a.75.75 0 1 1 1.04-1.08l5.5 5.25a.75.75 0 0 1 0 1.08l-5.5 5.25a.75.75 0 1 1-1.04-1.08l4.158-3.96H3.75A.75.75 0 0 1 3 10Z" clipRule="evenodd" />
          </svg>
        </Link>
        <Link href="/demo" className="inline-flex items-center justify-center gap-2 border border-zinc-700 hover:border-zinc-500 text-zinc-300 hover:text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 hover:-translate-y-0.5">
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 text-violet-400">
            <path d="M6.3 2.84A1.5 1.5 0 0 0 4 4.11v11.78a1.5 1.5 0 0 0 2.3 1.27l9.344-5.891a1.5 1.5 0 0 0 0-2.538L6.3 2.841Z" />
          </svg>
          Watch demo
        </Link>
      </div>
      <p className="relative z-10 mt-8 text-sm text-zinc-500 animate-fade-in-up [animation-delay:400ms]">
        Trusted by <span className="text-zinc-300 font-medium">2,400+ teams</span> worldwide
      </p>
    </section>
  );
}
