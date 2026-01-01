"use client";

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Check, X, Edit2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConversationTitleEditorProps {
  title: string | null;
  onSave: (title: string) => Promise<void>;
  className?: string;
  isSelected?: boolean;
}

export function ConversationTitleEditor({
  title,
  onSave,
  className,
  isSelected,
}: ConversationTitleEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(title || "");
  const [saving, setSaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setEditValue(title || "");
  }, [title]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleStartEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(true);
  };

  const handleSave = async () => {
    if (editValue.trim() === title) {
      setIsEditing(false);
      return;
    }

    try {
      setSaving(true);
      await onSave(editValue.trim() || "Untitled Conversation");
      setIsEditing(false);
    } catch (error) {
      // Error handling is done in parent component
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditValue(title || "");
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      handleCancel();
    }
  };

  if (isEditing) {
    return (
      <div className="flex items-center gap-1 flex-1 min-w-0" onClick={(e) => e.stopPropagation()}>
        <Input
          ref={inputRef}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={saving}
          className="h-6 text-sm px-2"
          onClick={(e) => e.stopPropagation()}
        />
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={handleSave}
          disabled={saving}
        >
          <Check className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          onClick={handleCancel}
          disabled={saving}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 flex-1 min-w-0 group">
      <p className={cn("text-sm font-medium truncate flex-1", className)}>
        {title || "Untitled Conversation"}
      </p>
      <Button
        variant="ghost"
        size="icon"
        className={cn(
          "h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity",
          isSelected && "text-primary-foreground hover:text-primary-foreground hover:bg-primary/80"
        )}
        onClick={handleStartEdit}
      >
        <Edit2 className="h-3 w-3" />
      </Button>
    </div>
  );
}

