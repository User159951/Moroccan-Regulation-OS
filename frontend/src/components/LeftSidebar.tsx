import { ChevronDown, ChevronRight, MessageCircle, Scale, BarChart3, Briefcase } from "lucide-react";
import { useState } from "react";
import type { TeamType } from "@/types/chat";

interface LeftSidebarProps {
  selectedTeam: TeamType;
  onTeamChange: (team: TeamType) => void;
}

export function LeftSidebar({ selectedTeam, onTeamChange }: LeftSidebarProps) {
  const [open, setOpen] = useState(true);

  const isActive = (team: TeamType) => selectedTeam === team;

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center mr-3">
            <Scale size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold">Régulation Maroc</h1>
            <p className="text-xs text-gray-400">Compliance & Finance</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-3">
        <div className="mt-4">
          <button
            className="flex items-center w-full px-3 py-2.5 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors text-sm"
            onClick={() => setOpen((o) => !o)}
          >
            <Scale size={16} className="mr-3 text-gray-300" />
            <span className="text-gray-300 flex-1">Régulation Assistants</span>
            {open ? (
              <ChevronDown size={14} className="text-gray-400" />
            ) : (
              <ChevronRight size={14} className="text-gray-400" />
            )}
          </button>

          {open && (
            <div className="ml-6 mt-1 space-y-0.5">
              {/* ACAPS (disabled) */}
              <button
                disabled
                className={`flex items-center w-full px-3 py-2 rounded-lg text-sm text-gray-500 cursor-not-allowed bg-transparent`}
              >
                <Scale size={14} className="mr-3" />
                <span>ACAPS</span>
              </button>
              {/* AMMC (disabled) */}
              <button
                disabled
                className={`flex items-center w-full px-3 py-2 rounded-lg text-sm text-gray-500 cursor-not-allowed bg-transparent`}
              >
                <BarChart3 size={14} className="mr-3" />
                <span>AMMC</span>
              </button>
              {/* Global (disabled like others) */}
              <button
                disabled
                className={`flex items-center w-full px-3 py-2 rounded-lg text-sm text-gray-500 cursor-not-allowed bg-transparent`}
              >
                <MessageCircle size={14} className="mr-3" />
                <span>Global</span>
              </button>
              {/* Senior Trade Manager (disabled like others) */}
              <button
                disabled
                className={`flex items-center w-full px-3 py-2 rounded-lg text-sm text-gray-500 cursor-not-allowed bg-transparent`}
              >
                <Briefcase size={14} className="mr-3" />
                <span>Senior Trade Manager</span>
              </button>
            </div>
          )}
        </div>
      </nav>
    </div>
  );
}

export default LeftSidebar;


