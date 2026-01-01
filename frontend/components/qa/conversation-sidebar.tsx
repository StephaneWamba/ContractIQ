"use client";

import { useState, useEffect } from "react";
import { api, Conversation } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Plus, MessageSquare, Trash2, Loader2, ChevronLeft, ChevronRight, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";
import { ConversationTitleEditor } from "./conversation-title-editor";

interface ConversationSidebarProps {
  workspaceId: string;
  selectedConversationId?: string;
  onConversationSelect: (conversationId: string) => void;
  onNewConversation: () => void;
}

export function ConversationSidebar({
  workspaceId,
  selectedConversationId,
  onConversationSelect,
  onNewConversation,
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const fetchConversations = async () => {
    if (!workspaceId) {
      setConversations([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await api.getConversations(workspaceId);
      // Filter out conversations without IDs (uncreated) and limit to 5 most recent
      const validConversations = data
        .filter((conv) => conv.id && conv.id.trim() !== "") // Filter uncreated conversations
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()) // Sort by most recent
        .slice(0, 5); // Limit to 5
      setConversations(validConversations);
    } catch (error: any) {
      toast.error("Failed to load conversations", {
        description: error.detail || "Please try again",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [workspaceId, selectedConversationId]); // Refresh when selected conversation changes

  const handleDelete = async (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation();
    
    if (!confirm("Are you sure you want to delete this conversation?")) return;

    try {
      setDeletingId(conversationId);
      await api.deleteConversation(conversationId);
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));
      
      if (selectedConversationId === conversationId) {
        onNewConversation();
      }
      
      toast.success("Conversation deleted");
    } catch (error: any) {
      toast.error("Failed to delete conversation", {
        description: error.detail || "Please try again",
      });
    } finally {
      setDeletingId(null);
    }
  };

  const handleTitleUpdate = async (conversationId: string, newTitle: string) => {
    try {
      const updated = await api.updateConversation(conversationId, newTitle);
      setConversations((prev) =>
        prev.map((c) => (c.id === conversationId ? updated : c))
      );
      toast.success("Title updated");
    } catch (error: any) {
      toast.error("Failed to update title", {
        description: error.detail || "Please try again",
      });
      throw error;
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col h-full border-r">
        <div className="p-4 border-b">
          <Skeleton className="h-10 w-full" />
        </div>
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </ScrollArea>
      </div>
    );
  }

  if (isCollapsed) {
    return (
      <div className="flex flex-col h-full border-r bg-muted/30 w-12 flex-shrink-0 transition-all duration-300">
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 m-2"
          onClick={() => setIsCollapsed(false)}
          title="Expand sidebar"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full border-r bg-muted/30 w-80 flex-shrink-0 transition-all duration-300">
      <div className="p-4 border-b flex items-center justify-between gap-2">
        <Button
          onClick={onNewConversation}
          className="flex-1"
          size="sm"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Conversation
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={() => setIsCollapsed(true)}
          title="Collapse sidebar"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 text-sm text-muted-foreground">
              <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No conversations yet</p>
              <p className="text-xs mt-1">Start a new conversation to begin</p>
            </div>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={cn(
                  "group relative p-3 rounded-lg cursor-pointer transition-colors",
                  selectedConversationId === conversation.id
                    ? "bg-primary text-primary-foreground"
                    : "bg-background hover:bg-accent"
                )}
                onClick={() => onConversationSelect(conversation.id)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <ConversationTitleEditor
                      title={conversation.title}
                      onSave={(title) => handleTitleUpdate(conversation.id, title)}
                      isSelected={selectedConversationId === conversation.id}
                      className={
                        selectedConversationId === conversation.id
                          ? "text-primary-foreground"
                          : ""
                      }
                    />
                    <p
                      className={cn(
                        "text-xs mt-1",
                        selectedConversationId === conversation.id
                          ? "text-primary-foreground/70"
                          : "text-muted-foreground"
                      )}
                    >
                      {formatDistanceToNow(new Date(conversation.updated_at), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    {selectedConversationId === conversation.id && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className={cn(
                          "h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity",
                          "text-primary-foreground hover:text-primary-foreground hover:bg-primary/80"
                        )}
                        onClick={async (e) => {
                          e.stopPropagation();
                          try {
                            const blob = await api.downloadConversationEvidencePack(conversation.id);
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url;
                            a.download = `conversation-evidence-pack-${conversation.id.slice(0, 8)}.pdf`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                            toast.success("Conversation evidence pack downloaded");
                          } catch (error: any) {
                            toast.error("Failed to download evidence pack", {
                              description: error.detail || "Please try again",
                            });
                          }
                        }}
                        title="Download full conversation evidence pack"
                      >
                        <Download className="h-3 w-3" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      className={cn(
                        "h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity",
                        selectedConversationId === conversation.id &&
                          "text-primary-foreground hover:text-primary-foreground hover:bg-primary/80"
                      )}
                      onClick={(e) => handleDelete(e, conversation.id)}
                      disabled={deletingId === conversation.id}
                    >
                      {deletingId === conversation.id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <Trash2 className="h-3 w-3" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

