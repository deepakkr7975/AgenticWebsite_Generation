"use client";
import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", message: "" });

  return (
    <main className="bg-[#09090B] text-[#F4F4F5] min-h-screen">
      <Navbar />
      <section className="pt-32 pb-24 px-6">
        <div className="max-w-xl mx-auto">
          <p className="text-sm font-semibold uppercase tracking-widest text-violet-400 mb-4">Contact</p>
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white mb-4">
            Get in touch
          </h1>
          <p className="text-zinc-400 mb-10">Questions, feedback, or want to book a demo?</p>
          {submitted ? (
            <div className="p-8 rounded-2xl border border-violet-500/30 bg-violet-500/10 text-center">
              <div className="text-4xl mb-4">✉️</div>
              <h2 className="text-xl font-bold text-white">Message sent!</h2>
              <p className="text-zinc-400 mt-2">We will get back to you within 24 hours.</p>
            </div>
          ) : (
            <div className="space-y-5">
              {[
                { id: "name", label: "Name", type: "text", placeholder: "Your name" },
                { id: "email", label: "Email", type: "email", placeholder: "you@company.com" },
              ].map((field) => (
                <div key={field.id}>
                  <label className="block text-sm font-medium text-zinc-300 mb-2">{field.label}</label>
                  <input type={field.type} placeholder={field.placeholder}
                    value={form[field.id as keyof typeof form]}
                    onChange={(e) => setForm({ ...form, [field.id]: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl border border-zinc-700 bg-zinc-900 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all" />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">Message</label>
                <textarea rows={5} placeholder="Tell us how we can help..."
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border border-zinc-700 bg-zinc-900 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all resize-none" />
              </div>
              <button onClick={() => setSubmitted(true)}
                className="w-full py-4 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold transition-all duration-200 hover:-translate-y-0.5">
                Send message →
              </button>
            </div>
          )}
        </div>
      </section>
      <Footer />
    </main>
  );
}
