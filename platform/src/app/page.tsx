"use client";

import { useState } from "react";
import { Header } from "@/components/landing/header";
import { Hero } from "@/components/landing/hero";
import { GL } from "@/components/gl";

export default function LandingPage() {
  const [hovering, setHovering] = useState(false);

  return (
    <main className="min-h-screen bg-background">
      <GL hovering={hovering} />
      <Header />
      <Hero onButtonHover={setHovering} />
    </main>
  );
}
