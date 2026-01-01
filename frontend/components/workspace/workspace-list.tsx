"use client";

import { useState, useEffect } from "react";
import { api, Workspace } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { 
  FolderOpen, 
  FileText, 
  MessageSquare, 
  Trash2, 
  Loader2,
  Plus,
  Calendar,
  MoreVertical
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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

interface WorkspaceListProps {
  onWorkspaceSelect?: (workspaceId: string) => void;
}

interface WorkspaceWithStats extends Workspace {
  documentCount?: number;
  conversationCount?: number;
}

export function WorkspaceList({ onWorkspaceSelect }: WorkspaceListProps) {
  const [workspaces, setWorkspaces] = useState<WorkspaceWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({ name: "", description: "" });
  const router = useRouter();

  const fetchWorkspaces = async () => {
    try {
      setLoading(true);
      const workspacesData = await api.getWorkspaces();
      
      // Fetch stats for each workspace
      const workspacesWithStats = await Promise.all(
        workspacesData.map(async (workspace) => {
          try {
            const documents = await api.getDocuments(workspace.id);
            const conversations = await api.getConversations(workspace.id);
            return {
              ...workspace,
              documentCount: Array.isArray(documents) ? documents.length : 0,
              conversationCount: Array.isArray(conversations) ? conversations.length : 0,
            };
          } catch (error) {
            return {
              ...workspace,
              documentCount: 0,
              conversationCount: 0,
            };
          }
        })
      );
      
      setWorkspaces(workspacesWithStats);
    } catch (error: any) {
      toast.error("Failed to load workspaces", {
        description: error.detail || "Please try again",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkspaces();
  }, []);

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
      setWorkspaces((prev) => [{ ...newWorkspace, documentCount: 0, conversationCount: 0 }, ...prev]);
      setCreateOpen(false);
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

  const handleDelete = async (workspaceId: string, workspaceName: string) => {
    if (!confirm(`Are you sure you want to delete "${workspaceName}"? This will delete all documents and conversations in this workspace.`)) {
      return;
    }

    try {
      setDeletingId(workspaceId);
      await api.deleteWorkspace(workspaceId);
      setWorkspaces((prev) => prev.filter((w) => w.id !== workspaceId));
      toast.success("Workspace deleted");
    } catch (error: any) {
      toast.error("Failed to delete workspace", {
        description: error.detail || "Please try again",
      });
    } finally {
      setDeletingId(null);
    }
  };

  const handleWorkspaceClick = (workspaceId: string) => {
    if (onWorkspaceSelect) {
      onWorkspaceSelect(workspaceId);
    } else {
      router.push(`/documents?workspaceId=${workspaceId}`);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-48 mt-2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Your Workspaces</h2>
          <p className="text-muted-foreground">
            Organize your contracts by project, client, or category
          </p>
        </div>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Workspace
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
              <Button variant="outline" onClick={() => setCreateOpen(false)}>
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

      {workspaces.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <FolderOpen className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
            <p className="text-sm font-medium mb-1">No workspaces yet</p>
            <p className="text-xs text-muted-foreground mb-4">
              Create your first workspace to get started
            </p>
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Workspace
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workspaces.map((workspace) => (
            <Card
              key={workspace.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => handleWorkspaceClick(workspace.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="flex items-center gap-2">
                      <FolderOpen className="h-5 w-5 text-primary" />
                      {workspace.name}
                    </CardTitle>
                    {workspace.description && (
                      <CardDescription className="mt-2">
                        {workspace.description}
                      </CardDescription>
                    )}
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          handleWorkspaceClick(workspace.id);
                        }}
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        View Documents
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(workspace.id, workspace.name);
                        }}
                        className="text-destructive"
                        disabled={deletingId === workspace.id}
                      >
                        {deletingId === workspace.id ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="mr-2 h-4 w-4" />
                        )}
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <FileText className="h-4 w-4" />
                      <span>Documents</span>
                    </div>
                    <Badge variant="secondary">
                      {workspace.documentCount || 0}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <MessageSquare className="h-4 w-4" />
                      <span>Conversations</span>
                    </div>
                    <Badge variant="secondary">
                      {workspace.conversationCount || 0}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2 border-t">
                    <Calendar className="h-3 w-3" />
                    <span>
                      Created {formatDistanceToNow(new Date(workspace.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

