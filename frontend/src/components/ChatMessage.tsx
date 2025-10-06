import { User, Bot } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Message } from "@/types/chat";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 mb-4 animate-in fade-in-0 slide-in-from-bottom-2",
        isUser && "flex-row-reverse"
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 rounded-full items-center justify-center",
          isUser ? "bg-primary" : "bg-muted"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-primary-foreground" />
        ) : (
          <Bot className="h-4 w-4 text-foreground" />
        )}
      </div>

      <div className={cn("flex flex-col gap-2 max-w-[75%]", isUser && "items-end")}>
        {/* Reasoning content (only for assistant) */}
        {!isUser && message.reasoning && (
          <div className="reasoning-frame animate-in fade-in-0 slide-in-from-bottom-2 duration-500">
            <div className="reasoning-title">
              <div className="reasoning-dot" />
              <span>Raisonnement</span>
              {message.isReasoning && (
                <span className="ml-2 text-xs opacity-75 animate-pulse">
                  En cours... {message.stepNumber && message.totalSteps ? 
                    `(${message.stepNumber}/${message.totalSteps})` : 
                    '(étape par étape)'
                  }
                </span>
              )}
            </div>
            <div 
              className="reasoning-content prose prose-sm max-w-none animate-in fade-in-0 slide-in-from-bottom-2 duration-500"
              dangerouslySetInnerHTML={{ __html: message.reasoning }}
              style={{ 
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                lineHeight: '1.4'
              }}
            />
          </div>
        )}

        {/* Main message */}
        <div
          className={cn(
            "rounded-lg px-4 py-3",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-chat-bot text-foreground"
          )}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          ) : (
            <div 
              className="text-sm leading-relaxed prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: message.content }}
            />
          )}
        </div>

        <span className="text-xs text-muted-foreground px-1">
          {new Date(message.timestamp).toLocaleTimeString("fr-FR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}
