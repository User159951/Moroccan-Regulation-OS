import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import type { TeamType, Team } from "@/types/chat";

// Teams will be loaded from API
const defaultTeams: Team[] = [
  {
    id: "global",
    name: "Team ACAPS + AMMC",
    description: "ACAPS + AMMC (Recommandé)",
    color: "primary",
  },
  {
    id: "acaps",
    name: "Agent ACAPS",
    description: "Autorité de Contrôle des Assurances",
    color: "secondary",
  },
  {
    id: "ammc",
    name: "Agent AMMC",
    description: "Autorité Marocaine du Marché des Capitaux",
    color: "accent",
  },
];

interface TeamSelectorProps {
  selectedTeam: TeamType;
  onTeamChange: (team: TeamType) => void;
}

export function TeamSelector({ selectedTeam, onTeamChange }: TeamSelectorProps) {
  const currentTeam = defaultTeams.find((t) => t.id === selectedTeam) || defaultTeams[0];

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="min-w-[180px] justify-start">
          <span className="font-medium">{currentTeam.name}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="p-3">
          <h3 className="text-sm font-semibold mb-3">Sélectionner une équipe</h3>
          <div className="space-y-1">
            {defaultTeams.map((team) => (
              <button
                key={team.id}
                onClick={() => onTeamChange(team.id)}
                className="w-full flex items-start gap-3 p-3 rounded-md hover:bg-muted transition-colors text-left"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{team.name}</span>
                    {team.id === selectedTeam && (
                      <Check className="h-4 w-4 text-primary" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {team.description}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
