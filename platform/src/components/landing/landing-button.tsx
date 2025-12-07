"use client";

import { cn } from "@/lib/utils";
import { px } from "./utils";
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex relative uppercase border font-mono cursor-pointer items-center font-medium ease-out transition-all duration-300 disabled:pointer-events-none disabled:opacity-50 outline-none [clip-path:polygon(var(--poly-roundness)_0,calc(100%_-_var(--poly-roundness))_0,100%_0,100%_calc(100%_-_var(--poly-roundness)),calc(100%_-_var(--poly-roundness))_100%,0_100%,0_calc(100%_-_var(--poly-roundness)),0_var(--poly-roundness))]",
  {
    variants: {
      variant: {
        default:
          "bg-background border-primary text-primary [box-shadow:inset_0_0_54px_0px_var(--tw-shadow-color)] shadow-[#EBB800] hover:shadow-[#EBB800]/80",
      },
      size: {
        default: "h-16 px-8 text-base tracking-widest",
        sm: "h-14 px-6 text-sm tracking-wider",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface LandingButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
}

export function LandingButton({
  className,
  variant,
  size,
  children,
  ...props
}: LandingButtonProps) {
  const polyRoundness = 16;
  const hypotenuse = polyRoundness * 2;
  const hypotenuseHalf = polyRoundness / 2 - 1.5;

  return (
    <button
      style={{ "--poly-roundness": px(polyRoundness) } as React.CSSProperties}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    >
      {/* Decorative corner borders */}
      <span
        aria-hidden="true"
        style={{ "--h": px(hypotenuse), "--hh": px(hypotenuseHalf) } as React.CSSProperties}
        className="absolute inline-block w-[var(--h)] top-[var(--hh)] left-[var(--hh)] h-[2px] -rotate-45 origin-top -translate-x-1/2 bg-primary"
      />
      <span
        aria-hidden="true"
        style={{ "--h": px(hypotenuse), "--hh": px(hypotenuseHalf) } as React.CSSProperties}
        className="absolute w-[var(--h)] bottom-[var(--hh)] right-[var(--hh)] h-[2px] -rotate-45 translate-x-1/2 bg-primary"
      />

      {children}
      <span className="ml-3">→</span>
    </button>
  );
}

