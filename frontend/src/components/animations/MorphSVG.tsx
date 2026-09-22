import React, { useEffect, useState } from 'react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { interpolate } from 'flubber';

// SVG Path definitions for smooth morphing:
// Path 1: Cooking Pot / Nồi nấu
const PATH_POT = "M20,40 C20,65 35,80 50,80 C65,80 80,65 80,40 L20,40 Z M15,35 L85,35 L85,40 L15,40 Z M45,25 L55,25 L55,35 L45,35 Z";

// Path 2: Food Bowl / Bát phở có đũa
const PATH_BOWL = "M15,45 C20,75 35,85 50,85 C65,85 80,75 85,45 L15,45 Z M35,85 L65,85 L60,92 L40,92 Z M30,30 C35,20 30,15 35,10 M50,30 C55,20 50,15 55,10 M70,30 C75,20 70,15 75,10";

// Path 3: Heart / Món ăn yêu thích
const PATH_HEART = "M50,85 C20,65 10,45 10,30 C10,18 20,10 32,10 C40,10 46,15 50,22 C54,15 60,10 68,10 C80,10 90,18 90,30 C90,45 80,65 50,85 Z";

const PATHS = [PATH_POT, PATH_BOWL, PATH_HEART];

interface MorphSVGProps {
  className?: string;
  size?: number;
  color?: string;
  autoPlay?: boolean;
  stepIndex?: number;
}

export const MorphSVG: React.FC<MorphSVGProps> = ({
  className = "",
  size = 64,
  color = "currentColor",
  autoPlay = true,
  stepIndex,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const progress = useMotionValue(0);

  useEffect(() => {
    if (stepIndex !== undefined) {
      setCurrentIndex(stepIndex % PATHS.length);
      return;
    }

    if (!autoPlay) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % PATHS.length);
    }, 2400);

    return () => clearInterval(interval);
  }, [autoPlay, stepIndex]);

  const nextIndex = (currentIndex + 1) % PATHS.length;
  
  // Create interpolation function between current path and next path
  const interpolator = interpolate(PATHS[currentIndex], PATHS[nextIndex], {
    maxSegmentLength: 2,
  });

  const path = useTransform(progress, [0, 1], [0, 1], {
    mixer: () => interpolator,
  });

  useEffect(() => {
    progress.set(0);
    const controls = animate(progress, 1, {
      duration: 1.2,
      ease: "easeInOut",
    });
    return () => controls.stop();
  }, [currentIndex]);

  return (
    <div className={`inline-flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
      <svg
        viewBox="0 0 100 100"
        width={size}
        height={size}
        className="overflow-visible filter drop-shadow-md"
      >
        <motion.path
          d={path}
          fill={color}
          initial={false}
          transition={{ duration: 1.2, ease: "easeInOut" }}
        />
      </svg>
    </div>
  );
};
