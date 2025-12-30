"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useWorkspaces } from "@/lib/api/hooks";

interface WorkspaceContextType {
  workspaceId: string | null;
  setWorkspaceId: (id: string | null) => void;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(
  undefined
);

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const { data: workspaces } = useWorkspaces();

  // Set first workspace as default if available
  useEffect(() => {
    if (!workspaceId && workspaces && workspaces.length > 0) {
      setWorkspaceId(workspaces[0].id);
    }
  }, [workspaceId, workspaces]);

  return (
    <WorkspaceContext.Provider value={{ workspaceId, setWorkspaceId }}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspaceContext() {
  const context = useContext(WorkspaceContext);
  if (context === undefined) {
    throw new Error("useWorkspaceContext must be used within WorkspaceProvider");
  }
  return context;
}


