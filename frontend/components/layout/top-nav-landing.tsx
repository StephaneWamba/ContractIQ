"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Github, Linkedin } from "lucide-react";

export function TopNavLanding() {
  return (
    <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="text-xl font-bold flex items-center gap-2">
            <span>ContractIQ</span>
          </Link>

          {/* Portfolio Badge */}
          <div className="flex items-center gap-4">
            <div className="px-3 py-1.5 rounded-full bg-amber-100 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800">
              <span className="text-xs font-medium text-amber-800 dark:text-amber-200">
                Portfolio Project
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm" className="hidden sm:flex">
              <Link href="https://github.com/StephaneWamba/ContractIQ" target="_blank" rel="noopener noreferrer">
                <Github className="h-4 w-4 mr-2" />
                GitHub
              </Link>
            </Button>
            <Button asChild variant="ghost" size="sm" className="hidden sm:flex">
              <Link href="https://www.linkedin.com/in/stephane-wamba/" target="_blank" rel="noopener noreferrer">
                <Linkedin className="h-4 w-4 mr-2" />
                LinkedIn
              </Link>
            </Button>
            <Button asChild size="sm">
              <Link href="/login">Sign In</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

