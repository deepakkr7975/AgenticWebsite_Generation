interface Plan { name: string; price: string; period: string; description: string; features: string[]; cta: string; highlighted: boolean; }

const plans: Plan[] = [
  { name: "Starter", price: "$0", period: "forever", description: "Perfect for individuals and small projects.", features: ["5 projects","10 team members","Basic analytics","2GB storage","Community support"], cta: "Get started free", highlighted: false },
  { name: "Pro", price: "$18", period: "per seat / month", description: "For growing teams that need more power.", features: ["Unlimited projects","Unlimited members","Advanced analytics","50GB storage","Git integration","Priority support"], cta: "Start Pro trial", highlighted: true },
  { name: "Enterprise", price: "Custom", period: "contact us", description: "Tailored for large orgs with compliance needs.", features: ["Everything in Pro","SSO & SAML","SOC 2 compliance","Dedicated CSM","Custom contracts","SLA guarantee"], cta: "Contact sales", highlighted: false },
];

export default function PricingSection() {
  return (
    <section className="py-24 px-6" id="pricing">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <p className="text-sm font-semibold uppercase tracking-widest text-violet-400 mb-4">Pricing</p>
          <h2 className="text-4xl sm:text-5xl font-black tracking-tight text-white" style={{ fontFamily: "'Clash Display', sans-serif" }}>
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-zinc-400 max-w-xl mx-auto">No hidden fees. Cancel anytime. Every plan includes a 14-day free trial.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
          {plans.map((plan) => (
            <div key={plan.name} className={`relative flex flex-col rounded-2xl p-8 border transition-all duration-300 ${plan.highlighted ? "bg-violet-600 border-violet-500 shadow-2xl shadow-violet-900/50 scale-105" : "bg-zinc-900/50 border-zinc-800 hover:border-zinc-700"}`}>
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-amber-400 text-zinc-900 text-xs font-bold uppercase tracking-wider px-4 py-1.5 rounded-full">Most popular</span>
                </div>
              )}
              <div>
                <h3 className={`text-lg font-bold ${plan.highlighted ? "text-white" : "text-zinc-300"}`}>{plan.name}</h3>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-5xl font-black tracking-tight text-white" style={{ fontFamily: "'Clash Display', sans-serif" }}>{plan.price}</span>
                  <span className={`text-sm ${plan.highlighted ? "text-violet-200" : "text-zinc-500"}`}>{plan.period}</span>
                </div>
                <p className={`mt-3 text-sm ${plan.highlighted ? "text-violet-200" : "text-zinc-400"}`}>{plan.description}</p>
              </div>
              <ul className="mt-8 flex-1 space-y-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-3 text-sm">
                    <svg viewBox="0 0 20 20" fill="currentColor" className={`w-5 h-5 flex-shrink-0 ${plan.highlighted ? "text-amber-300" : "text-violet-400"}`}>
                      <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z" clipRule="evenodd" />
                    </svg>
                    <span className={plan.highlighted ? "text-white" : "text-zinc-300"}>{f}</span>
                  </li>
                ))}
              </ul>
              <a href="/signup" className={`mt-8 block text-center py-3.5 px-6 rounded-xl font-semibold text-sm transition-all duration-200 hover:-translate-y-0.5 ${plan.highlighted ? "bg-white text-violet-700 hover:bg-zinc-100" : "bg-violet-600 hover:bg-violet-500 text-white"}`}>{plan.cta}</a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
