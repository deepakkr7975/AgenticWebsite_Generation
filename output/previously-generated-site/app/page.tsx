import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import FeaturesGrid from "@/components/FeaturesGrid";
import PricingSection from "@/components/PricingSection";
import CTABanner from "@/components/CTABanner";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "FlowForge — Ship Faster, Together",
  description: "The project management tool built for high-velocity teams.",
};

export default function LandingPage() {
  return (
    <main className="bg-[#09090B] text-[#F4F4F5] min-h-screen">
      <Navbar />
      <HeroSection />
      <FeaturesGrid />
      <PricingSection />
      <CTABanner />
      <Footer />
    </main>
  );
}
