import Navbar from "@/components/Navbar";
import FeaturesGrid from "@/components/FeaturesGrid";
import CTABanner from "@/components/CTABanner";
import Footer from "@/components/Footer";

export default function FeaturesPage() {
  return (
    <main className="bg-[#09090B] text-[#F4F4F5] min-h-screen">
      <Navbar />
      <div className="pt-24">
        <div className="text-center py-16 px-6">
          <p className="text-sm font-semibold uppercase tracking-widest text-violet-400 mb-4">All Features</p>
          <h1 className="text-5xl sm:text-6xl font-black tracking-tight text-white"
              style={{ fontFamily: "'Clash Display', sans-serif" }}>
            Everything you need <br />
            <span className="text-violet-400">to move fast</span>
          </h1>
        </div>
        <FeaturesGrid />
        <CTABanner />
      </div>
      <Footer />
    </main>
  );
}
