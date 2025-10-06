import { useState, useEffect, useRef } from "react";
import { useToast } from "@/hooks/use-toast";
import { ChatHeader } from "@/components/ChatHeader";
import { ChatContainer } from "@/components/ChatContainer";
import { ChatInput } from "@/components/ChatInput";
import { ChatFooter } from "@/components/ChatFooter";
import { HistorySidebar } from "@/components/HistorySidebar";
import { Terminal } from "@/components/Terminal";
import { api } from "@/lib/api";
import type { TeamType, Message, SessionInfo, WebSocketMessage } from "@/types/chat";

const Index = () => {
  const [selectedTeam, setSelectedTeam] = useState<TeamType>("global");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string>();
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [availableTeams, setAvailableTeams] = useState<{ teams: string[]; agents: string[] }>({ teams: [], agents: [] });
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const [currentReasoning, setCurrentReasoning] = useState<string>("");
  const [terminalContent, setTerminalContent] = useState("");
  const [isTerminalVisible, setIsTerminalVisible] = useState(false);
  const [isTerminalActive, setIsTerminalActive] = useState(false);
  const [currentStep, setCurrentStep] = useState("");
  const [stepNumber, setStepNumber] = useState<number>();
  const [totalSteps, setTotalSteps] = useState<number>();
  const wsRef = useRef<WebSocket | null>(null);
  const { toast } = useToast();

  // Check API health and initialize session on mount
  useEffect(() => {
    const checkHealthAndInitSession = async () => {
      try {
        await api.checkHealth();
        setIsConnected(true);
        
        // Initialiser une session si aucune n'existe
        if (!sessionId) {
          try {
            const sessionResult = await api.createSession();
            setSessionId(sessionResult.session_id);
            console.log('Session initialisée:', sessionResult.session_id);
            
            // Initialiser WebSocket
            initializeWebSocket(sessionResult.session_id);
          } catch (error) {
            console.error('Erreur lors de la création de session:', error);
          }
        }
      } catch (error) {
        setIsConnected(false);
        toast({
          title: "Erreur de connexion",
          description: "Impossible de se connecter au serveur. Vérifiez que l'API est démarrée.",
          variant: "destructive",
        });
      }
    };

    checkHealthAndInitSession();
    const interval = setInterval(checkHealthAndInitSession, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [toast, sessionId]);

  // Initialize WebSocket connection
  const initializeWebSocket = (sessionId: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    wsRef.current = api.connectWebSocket(
      sessionId,
      (data: WebSocketMessage) => {
        console.log('WebSocket message received:', data);
        
        if (data.type === "reasoning_start") {
          setCurrentReasoning(data.message || "Début de l'analyse...");
          setMessages(prev => [...prev, {
            id: `reasoning-${Date.now()}`,
            role: "assistant",
            content: "",
            reasoning: data.message || "Début de l'analyse...",
            timestamp: data.timestamp,
            isReasoning: true
          }]);
          // Terminal masqué - les étapes s'affichent dans le chat
          setIsTerminalVisible(false);
          setIsTerminalActive(false);
          setCurrentStep(""); // Reset du step
        } else if (data.type === "reasoning_step") {
          // Mettre à jour le terminal avec l'étape actuelle
          setCurrentStep(data.step || "");
          setStepNumber(data.step_number);
          setTotalSteps(data.total_steps);
          
          // Remplacer l'étape précédente par la nouvelle étape (pas d'accumulation)
          setCurrentReasoning(data.step || "");
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.isReasoning) {
              return [...prev.slice(0, -1), {
                ...lastMessage,
                reasoning: data.step || "", // Remplacer complètement, pas d'accumulation
                stepNumber: data.step_number,
                totalSteps: data.total_steps
              }];
            }
            return prev;
          });
        } else if (data.type === "response") {
          setCurrentReasoning("");
          
          // Terminal déjà masqué
          setCurrentStep("");
          
          // Délai avant de remplacer les étapes de raisonnement pour les laisser visibles
          setTimeout(() => {
            setMessages(prev => {
              // Remplacer le dernier message de raisonnement par la réponse finale
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.isReasoning) {
                return [...prev.slice(0, -1), {
                  id: `response-${Date.now()}`,
                  role: "assistant",
                  content: data.response || "",
                  reasoning: "", // Pas de reasoning dans la réponse finale
                  timestamp: data.timestamp,
                  isReasoning: false
                }];
              } else {
                // Si pas de message de raisonnement, ajouter normalement
                return [...prev, {
                  id: `response-${Date.now()}`,
                  role: "assistant",
                  content: data.response || "",
                  reasoning: "",
                  timestamp: data.timestamp
                }];
              }
            });
            setIsLoading(false);
          }, 3000); // 3 secondes de délai avant de remplacer
        }
      },
      (error: Event) => {
        console.error('WebSocket error:', error);
        setIsWebSocketConnected(false);
      },
      () => {
        console.log('WebSocket connected');
        setIsWebSocketConnected(true);
      },
      () => {
        console.log('WebSocket disconnected');
        setIsWebSocketConnected(false);
      }
    );
  };

  // Load sessions
  const loadSessions = async () => {
    try {
      const data = await api.getSessions();
      setSessions(data);
    } catch (error) {
      console.error("Failed to load sessions:", error);
    }
  };

  // Load available teams
  useEffect(() => {
    const loadTeams = async () => {
      try {
        const data = await api.getTeams();
        setAvailableTeams(data);
      } catch (error) {
        console.error("Failed to load teams:", error);
      }
    };

    if (isConnected) {
      loadTeams();
    }
  }, [isConnected]);

  useEffect(() => {
    if (isHistoryOpen) {
      loadSessions();
    }
  }, [isHistoryOpen]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSendMessage = async (content: string) => {
    if (!isConnected) {
      toast({
        title: "Erreur",
        description: "Pas de connexion au serveur",
        variant: "destructive",
      });
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Utiliser WebSocket si disponible, sinon fallback sur REST API
      if (isWebSocketConnected && wsRef.current && sessionId) {
        api.sendWebSocketMessage(wsRef.current, content, selectedTeam);
      } else {
        // Fallback sur REST API
        const response = await api.sendMessage({
          message: content,
          team: selectedTeam,
          session_id: sessionId,
        });

        setSessionId(response.session_id);

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response.response,
          reasoning: response.reasoning,
          timestamp: response.timestamp,
        };

        setMessages((prev) => [...prev, assistantMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible d'envoyer le message. Veuillez réessayer.",
        variant: "destructive",
      });
      // Remove the user message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
      setIsLoading(false);
    }
  };

  const handleSelectSession = async (id: string) => {
    try {
      setSessionId(id);
      const sessionData = await api.getSession(id);
      
      // Charger les messages de la session
      if ((sessionData as any).session_data && (sessionData as any).session_data.messages) {
        const loadedMessages: Message[] = (sessionData as any).session_data.messages.map((msg: any, index: number) => ({
          id: `${id}-${index}`,
          role: "user" as const,
          content: msg.user_message,
          timestamp: msg.timestamp,
        }));
        
        const assistantMessages: Message[] = (sessionData as any).session_data.messages.map((msg: any, index: number) => ({
          id: `${id}-${index}-bot`,
          role: "assistant" as const,
          content: msg.bot_response,
          reasoning: msg.reasoning,
          timestamp: msg.timestamp,
        }));
        
        const allMessages: Message[] = [...loadedMessages, ...assistantMessages];
        setMessages(allMessages);
      }
      
      toast({
        title: "Session chargée",
        description: "La session a été chargée avec succès.",
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de charger la session.",
        variant: "destructive",
      });
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await api.deleteSession(id);
      toast({
        title: "Session supprimée",
        description: "La session a été supprimée avec succès.",
      });
      loadSessions();
      if (sessionId === id) {
        setSessionId(undefined);
        setMessages([]);
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de supprimer la session.",
        variant: "destructive",
      });
    }
  };

  const handleExportSession = async (id: string) => {
    try {
      const blob = await api.exportPDF(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `session-${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast({
        title: "Export réussi",
        description: "Le PDF a été téléchargé avec succès.",
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible d'exporter la session en PDF.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      <ChatHeader
        selectedTeam={selectedTeam}
        onTeamChange={setSelectedTeam}
        onHistoryClick={() => setIsHistoryOpen(true)}
      />

      <ChatContainer messages={messages} isLoading={isLoading} />

      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />

      <ChatFooter isConnected={isConnected} currentTeam={selectedTeam} isWebSocketConnected={isWebSocketConnected} />

      <HistorySidebar
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        sessions={sessions}
        currentSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onExportSession={handleExportSession}
      />

      {/* Terminal masqué - les étapes s'affichent dans le chat */}
      {/* <Terminal 
        isVisible={isTerminalVisible}
        content={terminalContent}
        isActive={isTerminalActive}
        currentStep={currentStep}
        stepNumber={stepNumber}
        totalSteps={totalSteps}
      /> */}
    </div>
  );
};

export default Index;
