import { Download, Trash2, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { SessionInfo } from "@/types/chat";

interface SessionListProps {
  sessions: SessionInfo[];
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onExportSession: (sessionId: string) => void;
  currentSessionId?: string;
}

export function SessionList({
  sessions,
  onSelectSession,
  onDeleteSession,
  onExportSession,
  currentSessionId,
}: SessionListProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getTeamLabel = (team: string) => {
    const labels: Record<string, string> = {
      global: "Global",
      acaps: "ACAPS",
      ammc: "AMMC",
    };
    return labels[team] || team;
  };

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-3">
        {sessions.length === 0 ? (
          <div className="text-center py-8">
            <MessageSquare className="h-12 w-12 text-muted-foreground/50 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">
              Aucune session disponible
            </p>
          </div>
        ) : (
          sessions.map((session) => (
            <Card
              key={session.session_id}
              className={`p-4 cursor-pointer hover:bg-muted/50 transition-colors ${
                session.session_id === currentSessionId
                  ? "border-primary bg-primary/5"
                  : ""
              }`}
              onClick={() => onSelectSession(session.session_id)}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-muted-foreground">
                      {getTeamLabel(session.team_used)}
                    </span>
                    <span className="text-xs text-muted-foreground">•</span>
                    <span className="text-xs text-muted-foreground">
                      {session.message_count} messages
                    </span>
                  </div>
                  <p className="text-sm font-medium text-foreground truncate">
                    Session {formatDate(session.created_at)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Dernière activité: {formatDate(session.last_activity)}
                  </p>
                </div>
              </div>

              <div className="flex gap-2 mt-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onExportSession(session.session_id);
                  }}
                  className="flex-1"
                >
                  <Download className="h-3 w-3 mr-1" />
                  PDF
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.session_id);
                  }}
                  className="flex-1"
                >
                  <Trash2 className="h-3 w-3 mr-1" />
                  Supprimer
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>
    </ScrollArea>
  );
}
