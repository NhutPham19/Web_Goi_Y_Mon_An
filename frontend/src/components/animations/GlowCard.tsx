import React, { useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface GlowCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  glowColor?: string;
}

export const GlowCard: React.FC<GlowCardProps> = ({
  children,
  className,
  glowColor = "rgba(249, 115, 22, 0.15)",
  ...props
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn(
        "relative rounded-2xl border border-slate-200/80 bg-white/90 backdrop-blur-sm p-6 overflow-hidden transition-all duration-300 shadow-sm hover:shadow-xl hover:border-brand-300",
        className
      )}
      {...props}
    >
      {isHovered && (
        <div
          className="pointer-events-none absolute -inset-px transition-opacity duration-300"
          style={{
            background: `radial-gradient(400px circle at ${mousePosition.x}px ${mousePosition.y}px, ${glowColor}, transparent 70%)`,
          }}
        />
      )}
      <div className="relative z-10">{children}</div>
    </div>
  );
};
