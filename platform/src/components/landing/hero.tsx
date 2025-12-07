import Link from "next/link";
import { Pill } from "./pill";
import { LandingButton } from "./landing-button";

interface HeroProps {
  onButtonHover?: (hovering: boolean) => void;
}

export function Hero({ onButtonHover }: HeroProps) {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-4">
      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center max-w-4xl mx-auto">
        <Pill className="mb-8">Beta Release</Pill>

        <h1 className="text-5xl md:text-6xl lg:text-7xl font-extralight text-foreground mb-6 leading-tight">
          Automate recruiting
          <br />
          with <em className="font-light italic text-foreground/90">continuous</em> self-learning
        </h1>

        <p className="text-foreground/50 font-mono text-sm md:text-base max-w-lg mb-12 leading-relaxed tracking-wide">
          AI-powered sourcing that gets smarter with every candidate.
        </p>

        <Link href="/dashboard">
          <LandingButton
            onMouseEnter={() => onButtonHover?.(true)}
            onMouseLeave={() => onButtonHover?.(false)}
          >
            Get Started
          </LandingButton>
        </Link>
      </div>
    </section>
  );
}
