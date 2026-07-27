import type { ReactNode } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";
import { cn } from "../../utils/cn";

interface SectionCardProps {
  title: string;
  description?: string;
  children: ReactNode;
  headerAction?: ReactNode;
  className?: string;
}

export function SectionCard({ title, description, children, headerAction, className }: SectionCardProps) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
        <div>
          <CardTitle className="text-lg">{title}</CardTitle>
          {description && <p className="text-sm text-muted mt-1">{description}</p>}
        </div>
        {headerAction && <div>{headerAction}</div>}
      </CardHeader>
      <CardContent>
        {children}
      </CardContent>
    </Card>
  );
}
