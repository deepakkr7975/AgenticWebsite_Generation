import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function AboutPage() {
  const team = [
    { name: "Sofia Chen", role: "CEO & Co-founder", emoji: "👩‍💻" },
    { name: "Marcus Rivera", role: "CTO & Co-founder", emoji: "👨‍🔬" },
    { name: "Aisha Patel", role: "Head of Design", emoji: "🎨" },
    { name: "Tom Okafor", role: "Head of Engineering", emoji: "⚙️" },
  ];

  return (
    <main className="bg-[#09090B] text-[#F4F4F5] min-h-screen">
      <Navbar />
      <section className="pt-32 pb-20 px-6 text-center">
        <div className="max-w-4xl mx-auto">
          <p className="text-sm font-semibold uppercase tracking-widest text-violet-400 mb-4">Our Story</p>
          <h1 className="text-5xl sm:text-6xl font-black tracking-tight text-white mb-6"
              style={{ fontFamily: "'Clash Display', sans-serif" }}>
            We build tools for <br />
            <span className="text-violet-400">people who build</span>
          </h1>
          <p className="text-lg text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            FlowForge started in 2022 when our founders got tired of switching between
            10 different tools to ship a single feature. We built what we wished existed.
          </p>
        </div>
      </section>

      <section className="py-16 px-6 border-y border-zinc-800">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { value: "2,400+", label: "Teams" },
            { value: "120K+", label: "Tasks shipped" },
            { value: "99.9%", label: "Uptime" },
            { value: "4.9★", label: "Rating" },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-4xl font-black text-white">{stat.value}</div>
              <div className="mt-1 text-sm text-zinc-500">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-white mb-12 text-center">The team</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {team.map((member) => (
              <div key={member.name}
                   className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 text-center hover:border-zinc-700 transition-colors">
                <div className="text-5xl mb-4">{member.emoji}</div>
                <div className="text-sm font-semibold text-white">{member.name}</div>
                <div className="text-xs text-zinc-500 mt-1">{member.role}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
