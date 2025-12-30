"use client";

import { useState } from "react";
import { useConversation, useConversationMessages, useAskFollowUp } from "@/lib/api/hooks";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2 } from "lucide-react";
import { MessageBubble } from "./MessageBubble";
import { Skeleton } from "@/components/ui/skeleton";

interface ChatMessagesProps {
  conversationId: string;
}

export function ChatMessages({ conversationId }: ChatMessagesProps) {
  const [question, setQuestion] = useState("");
  const { data: conversation } = useConversation(conversationId);
  const { data: messages, isLoading } = useConversationMessages(conversationId);
  const askFollowUp = useAskFollowUp();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const questionText = question.trim();
    setQuestion("");

    try {
      await askFollowUp.mutateAsync({
        conversationId,
        question: questionText,
      });
    } catch (error) {
      console.error("Failed to ask question:", error);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4">
        <h2 className="font-semibold">
          {conversation?.title || "Conversation"}
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        ) : messages && messages.length > 0 ? (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>No messages yet. Ask your first question!</p>
          </div>
        )}

        {askFollowUp.isPending && (
          <div className="flex items-start gap-3">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Loader2 className="h-4 w-4 text-primary animate-spin" />
            </div>
            <Card>
              <CardContent className="p-3">
                <p className="text-sm">Thinking...</p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents..."
            disabled={askFollowUp.isPending}
            className="flex-1"
          />
          <Button type="submit" disabled={!question.trim() || askFollowUp.isPending}>
            {askFollowUp.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}


