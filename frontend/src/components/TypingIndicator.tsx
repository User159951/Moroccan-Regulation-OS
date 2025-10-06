import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex gap-3 mb-4 animate-in fade-in-0 slide-in-from-bottom-2">
      <div className="flex h-8 w-8 shrink-0 rounded-full items-center justify-center bg-muted">
        <Bot className="h-4 w-4 text-foreground" />
      </div>

      <div className="rounded-lg bg-chat-bot px-4 py-3">
        <div className="flex gap-1.5">
          <div className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce [animation-delay:-0.3s]" />
          <div className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce [animation-delay:-0.15s]" />
          <div className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce" />
        </div>
      </div>
    </div>
  );
}
