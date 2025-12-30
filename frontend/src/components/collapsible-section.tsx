"use client"

import { useState, ReactNode } from "react"
import { ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface CollapsibleSectionProps {
  title: string
  children: ReactNode
  defaultCollapsed?: boolean
  count?: number
  badge?: ReactNode
}

export function CollapsibleSection({
  title,
  children,
  defaultCollapsed = false,
  count,
  badge,
}: CollapsibleSectionProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed)

  return (
    <div className="border border-[#E5E5E5] bg-white rounded-md overflow-hidden">
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full flex items-center justify-between p-3 hover:bg-[#FAFAFA] transition-colors"
      >
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-black">{title}</h2>
          {count !== undefined && (
            <Badge variant="outline" className="text-xs">
              {count}
            </Badge>
          )}
          {badge}
        </div>
        <Button variant="ghost" size="icon" className="h-6 w-6">
          {isCollapsed ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronUp className="h-4 w-4" />
          )}
        </Button>
      </button>
      {!isCollapsed && <div className="p-3 pt-0">{children}</div>}
    </div>
  )
}


