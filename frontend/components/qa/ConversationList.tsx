"use client";

import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/lib/types";

interface ConversationListProps {
  conversations: Conversation[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function ConversationList({
  conversations,
  selectedId,
  onSelect,
}: ConversationListProps) {
  return (
    <div className="overflow-y-auto h-full">
      {conversations.length === 0 ? (
        <div className="p-4 text-center text-sm text-muted-foreground">
          No conversations yet
        </div>
      ) : (
        <div className="divide-y">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              onClick={() => onSelect(conversation.id)}
              className={cn(
                "w-full text-left p-4 hover:bg-accent transition-colors",
                selectedId === conversation.id && "bg-accent"
              )}
            >
              <div className="font-medium truncate mb-1">
                {conversation.title || "New Conversation"}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatDate(conversation.updated_at)}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}


