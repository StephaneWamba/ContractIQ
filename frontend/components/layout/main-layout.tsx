"use client";

import { TopNav } from "./top-nav";

export function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <TopNav />
      <main className="flex-1 overflow-y-auto bg-background">
        <div className="container mx-auto p-6">{children}</div>
      </main>
    </div>
  );
}

