"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { api, Conversation, Citation } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Send, Loader2, FileText, ExternalLink, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";
import ReactMarkdown from "react-markdown";

interface ChatInterfaceProps {
  workspaceId: string;
  conversationId?: string;
  onCitationClick?: (citation: Citation) => void;
  selectedDocumentIds?: string[];
  onConversationCreated?: (conversationId: string) => void;
  onMessageAdded?: () => void;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  createdAt: string;
}

export function ChatInterface({
  workspaceId,
  conversationId: initialConversationId,
  onCitationClick,
  selectedDocumentIds,
  onConversationCreated,
  onMessageAdded,
}: ChatInterfaceProps) {
  const [conversationId, setConversationId] = useState<string | undefined>(
    initialConversationId
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load conversation only if conversationId is provided
  useEffect(() => {
    if (conversationId && workspaceId) {
      loadConversation(conversationId);
    } else if (workspaceId && !conversationId) {
      // Don't auto-create - let user explicitly create via "New Conversation" button
      setMessages([]);
    }
  }, [workspaceId, conversationId]);

  const createNewConversation = async () => {
    try {
      const conv = await api.createConversation(workspaceId, "New Conversation");
      if (conv && conv.id) {
        setConversationId(conv.id);
        setMessages([]);
        // Notify parent component and update URL
        onConversationCreated?.(conv.id);
      } else {
        throw new Error("Conversation created but no ID returned");
      }
    } catch (error: any) {
      toast.error("Failed to create conversation", {
        description: error.detail || "Please try again",
      });
      // Reset conversation ID on error
      setConversationId(undefined);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      setLoadingHistory(true);
      const conv = await api.getConversation(id);
      const formattedMessages: Message[] = conv.messages.map((msg) => ({
        id: msg.id,
        role: msg.role as "user" | "assistant",
        content: msg.content,
        citations: msg.citations,
        createdAt: msg.created_at,
      }));
      setMessages(formattedMessages);
    } catch (error: any) {
      // If conversation not found (404), create a new one
      if (error.status === 404) {
        toast.error("Conversation not found", {
          description: "Creating a new conversation...",
        });
        setConversationId(undefined);
        if (workspaceId) {
          await createNewConversation();
        }
      } else {
        toast.error("Failed to load conversation", {
          description: error.detail || "Please try again",
        });
      }
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    // Ensure we have a conversation ID
    let currentConversationId = conversationId;
    if (!currentConversationId && workspaceId) {
      // Create conversation if we don't have one
      try {
        const conv = await api.createConversation(workspaceId, "New Conversation");
        if (conv && conv.id) {
          currentConversationId = conv.id;
          setConversationId(currentConversationId);
          onConversationCreated?.(currentConversationId);
        } else {
          toast.error("Failed to create conversation", {
            description: "Please try again",
          });
          return;
        }
      } catch (error: any) {
        toast.error("Failed to create conversation", {
          description: error.detail || "Please try again",
        });
        return;
      }
    }
    
    if (!currentConversationId) {
      toast.error("No conversation available", {
        description: "Please select a workspace first",
      });
      return;
    }

    const question = input.trim();
    setInput("");
    
    // Add user message immediately
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: question,
      createdAt: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      setLoading(true);
      const response = await api.askQuestion(currentConversationId, question, selectedDocumentIds);

      // Add assistant message
      const assistantMessage: Message = {
        id: response.message_id || `assistant-${Date.now()}`,
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => {
        // Replace temp user message with real one if needed
        const filtered = prev.filter((m) => !m.id.startsWith("temp-"));
        return [...filtered, userMessage, assistantMessage];
      });
      
      // Notify parent that a message was added (for sidebar refresh)
      onMessageAdded?.();
    } catch (error: any) {
      // If conversation not found (404), create a new one and retry
      if (error.status === 404 && workspaceId) {
        toast.error("Conversation not found", {
          description: "Creating a new conversation and retrying...",
        });
        try {
          const conv = await api.createConversation(workspaceId, "New Conversation");
          if (conv && conv.id) {
            setConversationId(conv.id);
            onConversationCreated?.(conv.id);
            // Retry the question with the new conversation
            const retryResponse = await api.askQuestion(conv.id, question, selectedDocumentIds);
            const assistantMessage: Message = {
              id: retryResponse.message_id || `assistant-${Date.now()}`,
              role: "assistant",
              content: retryResponse.answer,
              citations: retryResponse.citations,
              createdAt: new Date().toISOString(),
            };
            setMessages((prev) => {
              const filtered = prev.filter((m) => !m.id.startsWith("temp-"));
              return [...filtered, userMessage, assistantMessage];
            });
            return;
          }
        } catch (retryError: any) {
          toast.error("Failed to create new conversation", {
            description: retryError.detail || "Please try again",
          });
        }
      } else {
        toast.error("Failed to get answer", {
          description: error.detail || "Please try again",
        });
      }
      
      // Remove temp user message on error
      setMessages((prev) => prev.filter((m) => !m.id.startsWith("temp-")));
    } finally {
      setLoading(false);
    }
  };

  if (loadingHistory) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 p-4 space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Messages */}
      <ScrollArea className="flex-1 p-4 min-h-0" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-sm font-medium mb-1">Start a conversation</p>
              <p className="text-xs text-muted-foreground">
                Ask questions about your contracts
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {message.role === "assistant" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <FileText className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div
                  className={cn(
                    "rounded-lg px-4 py-2 max-w-[80%]",
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  )}
                >
                  {message.role === "assistant" ? (
                    <div className="text-sm prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                          li: ({ children }) => <li className="ml-2">{children}</li>,
                          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                          em: ({ children }) => <em className="italic">{children}</em>,
                          code: ({ children }) => (
                            <code className="bg-muted-foreground/20 px-1 py-0.5 rounded text-xs font-mono">
                              {children}
                            </code>
                          ),
                          h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                          h2: ({ children }) => <h2 className="text-base font-semibold mb-2">{children}</h2>,
                          h3: ({ children }) => <h3 className="text-sm font-semibold mb-1">{children}</h3>,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  )}
                  
                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-3 space-y-2 border-t pt-2">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-xs font-medium opacity-70">Sources:</p>
                        {conversationId && message.role === "assistant" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 px-2 text-xs"
                            onClick={async (e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              try {
                                const blob = await api.downloadEvidencePack(conversationId, message.id);
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement("a");
                                a.href = url;
                                a.download = `evidence-pack-${message.id.slice(0, 8)}.pdf`;
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                URL.revokeObjectURL(url);
                                toast.success("Evidence pack downloaded");
                              } catch (error: any) {
                                toast.error("Failed to download evidence pack", {
                                  description: error.detail || "Please try again",
                                });
                              }
                            }}
                          >
                            <Download className="h-3 w-3 mr-1" />
                            Download Evidence Pack
                          </Button>
                        )}
                      </div>
                      <div className="space-y-1">
                        {message.citations.map((citation, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-2 p-2 rounded-md hover:bg-accent/50 cursor-pointer transition-colors"
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              onCitationClick?.(citation);
                            }}
                          >
                            <ExternalLink className="h-3 w-3 mt-0.5 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium">
                                {citation.document_name}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                Page {citation.page_number} • {citation.section_name}
                              </p>
                              {citation.text_excerpt && (
                                <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                  {citation.text_excerpt}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs opacity-60 mt-2">
                    {formatDistanceToNow(new Date(message.createdAt), {
                      addSuffix: true,
                    })}
                  </p>
                </div>
                {message.role === "user" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-xs text-primary-foreground">U</span>
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <FileText className="h-4 w-4 text-primary" />
              </div>
              <div className="rounded-lg px-4 py-2 bg-muted">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-muted-foreground">
                    Thinking...
                  </span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your contracts..."
            disabled={loading || !workspaceId}
            className="flex-1"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <Button type="submit" disabled={loading || !workspaceId || !input.trim()}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}

