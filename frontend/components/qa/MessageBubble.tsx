"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { Citation } from "./Citation";
import type { ConversationMessage } from "@/lib/types";
import { User, Bot } from "lucide-react";

interface MessageBubbleProps {
  message: ConversationMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? "bg-primary text-primary-foreground" : "bg-primary/10 text-primary"
        }`}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      <div className={`flex-1 max-w-3xl ${isUser ? "flex flex-col items-end" : ""}`}>
        <Card className={isUser ? "bg-primary text-primary-foreground" : ""}>
          <CardContent className="p-4">
            <div className="whitespace-pre-wrap text-sm">{message.content}</div>
          </CardContent>
        </Card>

        {message.citations && message.citations.length > 0 && (
          <div className="mt-2 space-y-2">
            <p className="text-xs text-muted-foreground font-medium">Sources:</p>
            {message.citations.map((citation, index) => (
              <Citation key={index} citation={citation} />
            ))}
          </div>
        )}

        <p className="text-xs text-muted-foreground mt-1">
          {formatDate(message.created_at)}
        </p>
      </div>
    </div>
  );
}


