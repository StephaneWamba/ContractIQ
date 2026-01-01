"use client";

import { useState, useEffect, useCallback } from "react";
import { api, Workspace } from "@/lib/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Plus, Loader2 } from "lucide-react";

interface WorkspaceSelectorProps {
  value?: string;
  onValueChange: (workspaceId: string) => void;
}

export function WorkspaceSelector({
  value,
  onValueChange,
}: WorkspaceSelectorProps) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  });

  const fetchWorkspaces = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getWorkspaces();
      setWorkspaces(data);
      if (data.length > 0 && !value) {
        onValueChange(data[0].id);
      }
    } catch (error: any) {
      toast.error("Failed to load workspaces", {
        description: error.detail || "Please try again",
      });
    } finally {
      setLoading(false);
    }
  }, [value, onValueChange]);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const handleCreate = async () => {
    if (!formData.name.trim()) {
      toast.error("Workspace name is required");
      return;
    }

    try {
      setCreating(true);
      const newWorkspace = await api.createWorkspace({
        name: formData.name,
        description: formData.description || undefined,
      });
      setWorkspaces((prev) => [newWorkspace, ...prev]);
      onValueChange(newWorkspace.id);
      setOpen(false);
      setFormData({ name: "", description: "" });
      toast.success("Workspace created successfully");
    } catch (error: any) {
      toast.error("Failed to create workspace", {
        description: error.detail || "Please try again",
      });
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm text-muted-foreground">Loading workspaces...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="w-[250px]">
          <SelectValue placeholder="Select workspace" />
        </SelectTrigger>
        <SelectContent>
          {workspaces.map((workspace) => (
            <SelectItem key={workspace.id} value={workspace.id}>
              {workspace.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button variant="outline" size="icon">
            <Plus className="h-4 w-4" />
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Workspace</DialogTitle>
            <DialogDescription>
              Create a workspace to organize your contracts and documents.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="My Workspace"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                placeholder="Optional description"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={creating}>
              {creating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

