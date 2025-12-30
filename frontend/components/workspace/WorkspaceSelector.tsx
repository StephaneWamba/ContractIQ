"use client";

import { useWorkspaces } from "@/lib/api/hooks";
import { useWorkspaceContext } from "@/components/context/WorkspaceContext";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { CreateWorkspaceDialog } from "./CreateWorkspaceDialog";
import { useState } from "react";

export function WorkspaceSelector() {
  const { data: workspaces, isLoading } = useWorkspaces();
  const { workspaceId, setWorkspaceId } = useWorkspaceContext();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="h-10 w-full rounded-md border bg-muted animate-pulse" />
    );
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <Select
          value={workspaceId || undefined}
          onValueChange={(value) => setWorkspaceId(value)}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select workspace" />
          </SelectTrigger>
          <SelectContent>
            {workspaces?.map((workspace) => (
              <SelectItem key={workspace.id} value={workspace.id}>
                {workspace.name}
              </SelectItem>
            ))}
            <div className="border-t p-1">
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => setIsCreateDialogOpen(true)}
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Workspace
              </Button>
            </div>
          </SelectContent>
        </Select>
      </div>

      <CreateWorkspaceDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
      />
    </>
  );
}

