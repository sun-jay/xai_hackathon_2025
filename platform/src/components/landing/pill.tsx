import { cn } from "@/lib/utils";
import { px } from "./utils";

interface PillProps {
  children: React.ReactNode;
  className?: string;
}

export function Pill({ children, className }: PillProps) {
  const polyRoundness = 6;
  const hypotenuse = polyRoundness * 2;
  const hypotenuseHalf = polyRoundness / 2 - 1.5;

  return (
    <div
      style={{ "--poly-roundness": px(polyRoundness) } as React.CSSProperties}
      className={cn(
        "relative bg-[#262626]/50 transform-gpu font-medium text-foreground/50 backdrop-blur-sm font-mono text-sm inline-flex items-center justify-center px-4 h-9 border border-border",
        "[clip-path:polygon(var(--poly-roundness)_0,calc(100%_-_var(--poly-roundness))_0,100%_var(--poly-roundness),100%_calc(100%_-_var(--poly-roundness)),calc(100%_-_var(--poly-roundness))_100%,var(--poly-roundness)_100%,0_calc(100%_-_var(--poly-roundness)),0_var(--poly-roundness))]",
        className
      )}
    >
      {/* Corner decorations */}
      <span
        style={{ "--h": px(hypotenuse), "--hh": px(hypotenuseHalf) } as React.CSSProperties}
        className="absolute inline-block w-[var(--h)] top-[var(--hh)] left-[var(--hh)] h-[2px] -rotate-45 origin-top -translate-x-1/2 bg-border"
      />
      <span
        style={{ "--h": px(hypotenuse), "--hh": px(hypotenuseHalf) } as React.CSSProperties}
        className="absolute w-[var(--h)] top-[var(--hh)] right-[var(--hh)] h-[2px] bg-border rotate-45 translate-x-1/2"
      />
      <span
        style={{ "--h": px(hypotenuse), "--hh": px(hypotenuseHalf) } as React.CSSProperties}
        className="absolute w-[var(--h)] bottom-[var(--hh)] left-[var(--hh)] h-[2px] bg-border rotate-45 -translate-x-1/2"
      />
      <span
        style={{ "--h": px(hypotenuse), "--hh": px(hypotenuseHalf) } as React.CSSProperties}
        className="absolute w-[var(--h)] bottom-[var(--hh)] right-[var(--hh)] h-[2px] bg-border -rotate-45 translate-x-1/2"
      />

      {/* Glowing dot indicator */}
      <span className="inline-block size-2.5 rounded-full bg-primary mr-2 shadow-[0_0_8px_2px] shadow-primary/50" />

      <span className="uppercase tracking-wider">{children}</span>
    </div>
  );
}

