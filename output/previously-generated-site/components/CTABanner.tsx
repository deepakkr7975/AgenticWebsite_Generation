import Link from "next/link";

export default function CTABanner() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-4xl mx-auto rounded-3xl overflow-hidden relative"
           style={{ background: "linear-gradient(135deg, #4C1D95 0%, #7C3AED 50%, #6D28D9 100%)" }}>
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: "radial-gradient(circle at 20% 50%, #F59E0B 0%, transparent 50%), radial-gradient(circle at 80% 50%, #A78BFA 0%, transparent 50%)" }} />
        <div className="relative z-10 text-center py-16 px-8">
          <h2 className="text-4xl sm:text-5xl font-black text-white tracking-tight" style={{ fontFamily: "'Clash Display', sans-serif" }}>
            Ready to ship faster?
          </h2>
          <p className="mt-4 text-violet-200 text-lg max-w-xl mx-auto">
            Join 2,400+ teams already using FlowForge. Get started for free — no credit card required.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="inline-flex items-center justify-center gap-2 bg-white text-violet-700 hover:bg-zinc-100 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 hover:-translate-y-0.5">
              Start for free →
            </Link>
            <Link href="/contact" className="inline-flex items-center justify-center gap-2 border border-white/30 hover:border-white/60 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200">
              Talk to sales
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
