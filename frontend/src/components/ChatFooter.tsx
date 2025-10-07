import { Circle } from "lucide-react";
import type { TeamType } from "@/types/chat";

interface ChatFooterProps {
  isConnected: boolean;
  currentTeam: TeamType;
  isWebSocketConnected?: boolean;
}

export function ChatFooter({ isConnected, currentTeam, isWebSocketConnected = false }: ChatFooterProps) {
  // Removed active team label per request

  return (
    <footer className="border-t bg-card">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <Circle
              className={`h-2 w-2 fill-current ${
                isConnected ? "text-secondary" : "text-destructive"
              }`}
            />
            <span className="text-muted-foreground">
              {isConnected ? "Connecté" : "Déconnecté"}
            </span>
            {isWebSocketConnected && (
              <>
                <Circle className="h-2 w-2 fill-current text-primary" />
                <span className="text-muted-foreground text-xs">
                  WebSocket actif
                </span>
              </>
            )}
          </div>

          <div />
        </div>
      </div>
    </footer>
  );
}
