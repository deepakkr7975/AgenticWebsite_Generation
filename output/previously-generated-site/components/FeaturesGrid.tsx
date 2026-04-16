interface Feature { icon: string; title: string; description: string; }

const features: Feature[] = [
  { icon: "⚡", title: "Lightning fast", description: "Sub-second load times with edge rendering. Your team will never wait." },
  { icon: "🔀", title: "Git-integrated sprints", description: "Auto-link PRs, branches, and commits to tasks. Ship with context." },
  { icon: "📊", title: "Real-time dashboards", description: "Live velocity, burndown, and cycle time metrics — no config needed." },
  { icon: "🤝", title: "Async-first collaboration", description: "Rich comments, video clips, and threaded discussions on every task." },
  { icon: "🔔", title: "Smart notifications", description: "Only get pinged when it actually matters. AI filters the noise." },
  { icon: "🔒", title: "Enterprise security", description: "SOC 2 Type II, SSO, SAML, and granular permissions out of the box." },
];

export default function FeaturesGrid() {
  return (
    <section className="py-24 px-6" id="features">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-sm font-semibold uppercase tracking-widest text-violet-400 mb-4">Why FlowForge</p>
          <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-white" style={{ fontFamily: "'Clash Display', sans-serif" }}>
            Built for speed, <br /><span className="text-zinc-400">designed for clarity</span>
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="group relative p-6 rounded-2xl border border-zinc-800 bg-zinc-900/50 hover:bg-zinc-900 hover:border-zinc-700 transition-all duration-300 cursor-default">
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-br from-violet-600/5 to-transparent" />
              <div className="relative z-10">
                <span className="text-3xl">{f.icon}</span>
                <h3 className="mt-4 text-lg font-semibold text-white">{f.title}</h3>
                <p className="mt-2 text-sm text-zinc-400 leading-relaxed">{f.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
