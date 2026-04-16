import Navbar from "@/components/Navbar";
import PricingSection from "@/components/PricingSection";
import CTABanner from "@/components/CTABanner";
import Footer from "@/components/Footer";

export default function PricingPage() {
  return (
    <main className="bg-[#09090B] text-[#F4F4F5] min-h-screen">
      <Navbar />
      <div className="pt-24">
        <PricingSection />
        <CTABanner />
      </div>
      <Footer />
    </main>
  );
}
