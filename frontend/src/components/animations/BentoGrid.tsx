import React from 'react';
import { cn } from '@/lib/utils';

export const BentoGrid = ({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) => {
  return (
    <div
      className={cn(
        "grid md:auto-rows-[18rem] grid-cols-1 md:grid-cols-3 gap-4 max-w-7xl mx-auto",
        className
      )}
    >
      {children}
    </div>
  );
};

export const BentoGridItem = ({
  className,
  title,
  description,
  header,
  icon,
  onClick,
  badge,
}: {
  className?: string;
  title?: string | React.ReactNode;
  description?: string | React.ReactNode;
  header?: React.ReactNode;
  icon?: React.ReactNode;
  onClick?: () => void;
  badge?: string;
}) => {
  return (
    <div
      onClick={onClick}
      className={cn(
        "row-span-1 rounded-2xl group/bento hover:shadow-2xl transition duration-300 shadow-input dark:shadow-none p-4 dark:bg-black dark:border-white/[0.2] bg-white border border-slate-100 justify-between flex flex-col space-y-4 relative overflow-hidden cursor-pointer hover:-translate-y-1",
        className
      )}
    >
      {badge && (
        <span className="absolute top-3 right-3 z-10 bg-brand-500/90 backdrop-blur-sm text-white text-xs font-semibold px-2.5 py-1 rounded-full shadow-sm">
          {badge}
        </span>
      )}
      <div className="overflow-hidden rounded-xl h-full w-full relative">
        {header}
      </div>
      <div className="group-hover/bento:translate-x-1 transition duration-200">
        <div className="flex items-center gap-2 mb-1">
          {icon}
          <div className="font-sans font-bold text-neutral-800 dark:text-neutral-200 line-clamp-1">
            {title}
          </div>
        </div>
        <div className="font-sans font-normal text-neutral-600 text-xs dark:text-neutral-300 line-clamp-2">
          {description}
        </div>
      </div>
    </div>
  );
};
