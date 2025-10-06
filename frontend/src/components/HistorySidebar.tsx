import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { SessionList } from "./SessionList";
import type { SessionInfo } from "@/types/chat";

interface HistorySidebarProps {
  isOpen: boolean;
  onClose: () => void;
  sessions: SessionInfo[];
  currentSessionId?: string;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onExportSession: (sessionId: string) => void;
}

export function HistorySidebar({
  isOpen,
  onClose,
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
  onExportSession,
}: HistorySidebarProps) {
  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:w-[400px] p-0">
        <SheetHeader className="border-b p-4">
          <div className="flex items-center justify-between">
            <SheetTitle>Historique des sessions</SheetTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </SheetHeader>

        <SessionList
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={(id) => {
            onSelectSession(id);
            onClose();
          }}
          onDeleteSession={onDeleteSession}
          onExportSession={onExportSession}
        />
      </SheetContent>
    </Sheet>
  );
}
