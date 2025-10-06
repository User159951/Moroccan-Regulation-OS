import { MessageSquare, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TeamSelector } from "./TeamSelector";
import type { TeamType } from "@/types/chat";

interface ChatHeaderProps {
  selectedTeam: TeamType;
  onTeamChange: (team: TeamType) => void;
  onHistoryClick: () => void;
}

export function ChatHeader({ selectedTeam, onTeamChange, onHistoryClick }: ChatHeaderProps) {
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageSquare className="h-6 w-6 text-primary" />
            <div>
              <h1 className="text-lg font-semibold text-foreground">
                Chatbot Régulation Marocaine
              </h1>
              <p className="text-xs text-muted-foreground">
                Assistant ACAPS & AMMC
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <TeamSelector selectedTeam={selectedTeam} onTeamChange={onTeamChange} />
            <Button variant="outline" size="sm" onClick={onHistoryClick}>
              <History className="h-4 w-4 mr-2" />
              Historique
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
