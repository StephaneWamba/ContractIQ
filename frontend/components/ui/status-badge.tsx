"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { CheckCircle2, Loader2, XCircle, Clock } from "lucide-react";

interface StatusBadgeProps {
  status: "pending" | "uploaded" | "processing" | "processed" | "failed";
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = {
    pending: {
      label: "Pending",
      icon: Clock,
      variant: "secondary" as const,
      color: "bg-[var(--status-info)] text-white",
    },
    uploaded: {
      label: "Uploaded",
      icon: Clock,
      variant: "secondary" as const,
      color: "bg-[var(--status-info)] text-white",
    },
    processing: {
      label: "Processing",
      icon: Loader2,
      variant: "secondary" as const,
      color: "bg-[var(--status-warning)] text-white",
    },
    processed: {
      label: "Processed",
      icon: CheckCircle2,
      variant: "default" as const,
      color: "bg-[var(--status-success)] text-white",
    },
    failed: {
      label: "Failed",
      icon: XCircle,
      variant: "destructive" as const,
      color: "bg-[var(--status-error)] text-white",
    },
  };

  // Handle unknown status values gracefully
  const statusConfig = config[status as keyof typeof config] || config.pending;
  const { label, icon: Icon, variant, color } = statusConfig;

  return (
    <Badge
      variant={variant}
      className={cn("font-medium gap-1.5", color, className)}
    >
      <Icon
        className={cn(
          "h-3.5 w-3.5",
          status === "processing" && "animate-spin"
        )}
      />
      {label}
    </Badge>
  );
}

