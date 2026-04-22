"use client";

import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

export type CardShellProps = HTMLMotionProps<"div"> & {
  delay?: number;
};

export function CardShell({ className, delay = 0, children, ...rest }: CardShellProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: [0.22, 1, 0.36, 1] }}
      className={cn("cp-card p-5", className)}
      {...rest}
    >
      {children}
    </motion.div>
  );
}
