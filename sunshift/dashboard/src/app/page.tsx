import { LandingHeader } from '@/components/landing/LandingHeader';
import { HeroSection } from '@/components/landing/HeroSection';
import { RealityCheckSection } from '@/components/landing/RealityCheckSection';
import { FeaturesSection } from '@/components/landing/FeaturesSection';
import { ArchitectureSection } from '@/components/landing/ArchitectureSection';
import { PricingSection } from '@/components/landing/PricingSection';
import { DocsSection } from '@/components/landing/DocsSection';
import { LandingFooter } from '@/components/landing/LandingFooter';

export default function RootPage() {
  return (
    <>
      <LandingHeader />
      <main className="overflow-hidden">
        <HeroSection />
        <RealityCheckSection />
        <FeaturesSection />
        <ArchitectureSection />
        <PricingSection />
        <DocsSection />
      </main>
      <LandingFooter />
    </>
  );
}
