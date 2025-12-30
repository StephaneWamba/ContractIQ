"use client";

import { useState } from "react";
import { useWorkspaceContext } from "@/components/context/WorkspaceContext";
import { useConversations, useCreateConversation, useAskQuestion } from "@/lib/api/hooks";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Plus } from "lucide-react";
import { ConversationList } from "./ConversationList";
import { ChatMessages } from "./ChatMessages";
import { cn } from "@/lib/utils";

export function QAChatInterface() {
  const { workspaceId } = useWorkspaceContext();
  const { data: conversations } = useConversations(workspaceId || "");
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const createConversation = useCreateConversation();

  const handleNewConversation = async () => {
    if (!workspaceId) return;
    try {
      const conversation = await createConversation.mutateAsync({
        workspace_id: workspaceId,
      });
      setSelectedConversationId(conversation.id);
    } catch (error) {
      console.error("Failed to create conversation:", error);
    }
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] gap-6">
      <div className="w-80 border-r">
        <div className="p-4 border-b">
          <Button onClick={handleNewConversation} className="w-full" disabled={!workspaceId}>
            <Plus className="h-4 w-4 mr-2" />
            New Conversation
          </Button>
        </div>
        <ConversationList
          conversations={conversations || []}
          selectedId={selectedConversationId}
          onSelect={setSelectedConversationId}
        />
      </div>
      <div className="flex-1 flex flex-col">
        {selectedConversationId ? (
          <ChatMessages conversationId={selectedConversationId} />
        ) : (
          <Card className="flex-1 flex items-center justify-center">
            <CardContent className="text-center">
              <p className="text-muted-foreground mb-4">
                Select a conversation or create a new one to start asking questions
              </p>
              <Button onClick={handleNewConversation} disabled={!workspaceId}>
                <Plus className="h-4 w-4 mr-2" />
                New Conversation
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}


