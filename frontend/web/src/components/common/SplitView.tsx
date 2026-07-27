import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

interface SplitViewProps {
  master: ReactNode;
  detail: ReactNode;
  masterWidth?: string;
  className?: string;
  showDetailOnMobile?: boolean;
}

export function SplitView({
  master,
  detail,
  masterWidth = "w-full md:w-1/3 lg:w-[400px]",
  className,
  showDetailOnMobile = false
}: SplitViewProps) {
  return (
    <div className={cn("flex flex-col md:flex-row h-full w-full gap-4 relative", className)}>
      <div
        className={cn(
          "shrink-0 h-full overflow-y-auto overflow-x-hidden border border-border rounded-xl bg-surface shadow-sm",
          masterWidth,
          showDetailOnMobile ? "hidden md:block" : "block"
        )}
      >
        {master}
      </div>
      <div
        className={cn(
          "flex-1 h-full min-w-0 overflow-y-auto overflow-x-hidden border border-border rounded-xl bg-surface shadow-sm relative",
          !showDetailOnMobile ? "hidden md:block" : "block"
        )}
      >
        {detail}
      </div>
    </div>
  );
}
