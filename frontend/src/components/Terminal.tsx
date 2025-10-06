import React from 'react';
import { cn } from '@/lib/utils';

interface TerminalProps {
  isVisible: boolean;
  content: string;
  isActive: boolean;
  currentStep?: string;
  stepNumber?: number;
  totalSteps?: number;
}

export function Terminal({ isVisible, content, isActive, currentStep, stepNumber, totalSteps }: TerminalProps) {
  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-64 bg-black text-green-400 font-mono text-xs rounded-lg shadow-2xl border border-gray-600 z-50">
      {/* Terminal Header */}
      <div className="bg-gray-800 px-3 py-2 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
        </div>
        <span className="text-gray-400 text-xs">
          Agent Terminal {stepNumber && totalSteps ? `(${stepNumber}/${totalSteps})` : ''}
        </span>
      </div>
      
      {/* Terminal Content - Afficher uniquement les reasoning steps */}
      <div className="p-3 h-full overflow-y-auto">
        <div className="space-y-1">
          {currentStep ? (
            <div className="text-green-400 whitespace-pre-wrap">
              {currentStep}
            </div>
          ) : (
            <div className="text-green-300">$ Waiting for reasoning steps...</div>
          )}
          {isActive && (
            <div className="flex items-center gap-1">
              <span className="text-green-400">$</span>
              <div className="w-2 h-4 bg-green-400 animate-pulse"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
