import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  showText?: boolean;
}

export function Logo({ className, showText = true }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      {/* xAI / Grok Logo */}
      <svg
        width="32"
        height="32"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="text-foreground"
      >
        <path
          d="M2.5 4L9.5 12L2.5 20H6L11 14L16 20H19.5L12.5 12L19.5 4H16L11 10L6 4H2.5Z"
          fill="currentColor"
        />
        <path
          d="M18 4H21.5L14.5 12L21.5 20H18"
          stroke="currentColor"
          strokeWidth="1.5"
          fill="none"
        />
      </svg>
      {showText && (
        <span className="text-xl font-medium text-foreground tracking-wide">
          Grok Recruiter
        </span>
      )}
    </div>
  );
}

