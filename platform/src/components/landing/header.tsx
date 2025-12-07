import Link from "next/link";
import { Logo } from "./logo";

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      <div className="container flex items-center justify-between h-20">
        <Logo />
        <nav>
          <Link
            href="/dashboard"
            className="text-primary font-mono text-sm uppercase tracking-widest hover:text-primary/80 transition-colors"
          >
            Sign In
          </Link>
        </nav>
      </div>
    </header>
  );
}

