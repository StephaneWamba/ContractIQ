"use client"

import { Moon, Sun, Settings, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface HeaderProps {
  workspaceName?: string
}

export function Header({ workspaceName }: HeaderProps) {
  const [darkMode, setDarkMode] = useState(false)

  return (
    <header className="flex h-14 items-center justify-between border-b border-[#E5E5E5] bg-white px-6">
      <div className="flex items-center gap-3">
        {workspaceName && (
          <>
            <span className="text-sm text-[#404040]">Workspace:</span>
            <span className="text-sm font-medium text-black">{workspaceName}</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setDarkMode(!darkMode)}
          className="h-8 w-8"
        >
          {darkMode ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Settings className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <User className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}

