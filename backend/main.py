import os
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Console output
    ]
)
logger = logging.getLogger(__name__)

# Custom debug function for agent outputs
def debug_log(message: str, data=None):
    """Enhanced logging function for debugging agent interactions"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*80}")
    print(f"📊 [{timestamp}] {message}")
    if data:
        if isinstance(data, dict):
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(str(data))
    print('='*80 + "\n")

# Enhanced output cleaning function
def clean_agent_output(content: str) -> str:
    """Clean and format agent output for better HTML presentation"""
    import re
    
    if not content:
        return ""
    
    # Check if content is already HTML (contains HTML tags with classes)
    is_html = bool(re.search(r'<\s*(p|div|h[1-6]|ul|ol|li|table|strong|em|a|code|pre)\b[^>]*class=', content, re.IGNORECASE))
    
    if is_html:
        # Content is already HTML with classes, return as-is
        debug_log("CONTENT IS ALREADY HTML WITH CLASSES", {
            "preview": content[:200] + "..." if len(content) > 200 else content
        })
        return content
    
    # Clean up common formatting issues first
    cleaned = content
    cleaned = cleaned.strip()  # Trim whitespace
    cleaned = re.sub(r'\s+\n', '\n', cleaned)  # Remove trailing spaces before line breaks
    cleaned = re.sub(r'\n\s+', '\n', cleaned)  # Remove leading spaces after line breaks
    
    # Fix tables first
    cleaned = re.sub(r'\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|', 
                     r'<tr><td class="px-4 py-2 border-b border-gray-200 font-medium">\1</td><td class="px-4 py-2 border-b border-gray-200">\2</td><td class="px-4 py-2 border-b border-gray-200 font-semibold text-primary-600">\3</td></tr>', 
                     cleaned)
    cleaned = re.sub(r'\|([^|\n]+)\|([^|\n]+)\|', 
                     r'<tr><td class="px-4 py-2 border-b border-gray-200 font-medium">\1</td><td class="px-4 py-2 border-b border-gray-200 font-semibold text-primary-600">\2</td></tr>', 
                     cleaned)
    cleaned = re.sub(r'\|([^|\n]+)\|', 
                     r'<th class="px-4 py-3 bg-gray-50 font-semibold text-gray-900 text-left">\1</th>', 
                     cleaned)
    cleaned = re.sub(r'\|--+\|', '', cleaned)
    cleaned = re.sub(r'(<th[^>]*>.*?</th>)', r'<thead><tr>\1</tr></thead>', cleaned)
    cleaned = re.sub(r'(<tr[^>]*>.*?</tr>)', r'<tbody>\1</tbody>', cleaned)
    cleaned = re.sub(r'(<thead>.*?</thead>)(<tbody>.*?</tbody>)', 
                     r'<table class="w-full border-collapse border border-gray-300 rounded-lg overflow-hidden shadow-sm mb-6">\1\2</table>', 
                     cleaned)
    cleaned = re.sub(r'(<tbody>.*?</tbody>)', 
                     r'<table class="w-full border-collapse border border-gray-300 rounded-lg overflow-hidden shadow-sm mb-6"><tbody>\1</tbody></table>', 
                     cleaned)
    
    # Fix headings with better cleaning
    def replace_heading(match):
        level = len(match.group(1))
        content = match.group(2).strip()
        if level == 1:
            return f'<h1 class="text-2xl font-bold text-gray-900 mb-4 mt-6 border-b border-gray-200 pb-2">{content}</h1>'
        elif level == 2:
            return f'<h2 class="text-xl font-semibold text-gray-900 mb-3 mt-5">{content}</h2>'
        elif level == 3:
            return f'<h3 class="text-lg font-semibold text-gray-900 mb-3 mt-4 border-b border-gray-200 pb-1">{content}</h3>'
        else:
            return f'<h{level} class="text-lg font-semibold text-gray-900 mb-2 mt-3">{content}</h{level}>'
    
    cleaned = re.sub(r'^(#{1,6})\s*(.*?)$', replace_heading, cleaned, flags=re.MULTILINE)
    
    # Fix bullet points and lists
    cleaned = re.sub(r'^[-*+]\s+(.*?)$', r'<li class="mb-2 ml-4 list-disc">\1</li>', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'^\d+\.\s+(.*?)$', r'<li class="mb-2 ml-4 list-decimal">\1</li>', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'(<li[^>]*>.*?</li>)', r'<ul class="mb-4 ml-4 list-disc space-y-1">\1</ul>', cleaned)
    
    # Fix bold and italic
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-semibold text-gray-900">\1</strong>', cleaned)
    cleaned = re.sub(r'\*(.*?)\*', r'<em class="italic text-gray-800">\1</em>', cleaned)
    cleaned = re.sub(r'__(.*?)__', r'<strong class="font-semibold text-gray-900">\1</strong>', cleaned)
    cleaned = re.sub(r'_(.*?)_', r'<em class="italic text-gray-800">\1</em>', cleaned)
    
    # Fix code blocks
    cleaned = re.sub(r'```([\s\S]*?)```', r'<pre class="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4 font-mono"><code>\1</code></pre>', cleaned)
    cleaned = re.sub(r'`([^`]+)`', r'<code class="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono">\1</code>', cleaned)
    
    # Fix blockquotes
    cleaned = re.sub(r'^>\s*(.*?)$', r'<blockquote class="border-l-4 border-primary-300 pl-4 italic text-gray-700 mb-4 bg-gray-50 py-2 rounded-r">\1</blockquote>', cleaned, flags=re.MULTILINE)
    
    # Fix horizontal rules
    cleaned = re.sub(r'^[-*_]{3,}$', r'<hr class="my-6 border-gray-300">', cleaned, flags=re.MULTILINE)
    
    # Clean up paragraphs and line breaks - preserve natural formatting
    cleaned = re.sub(r'\n\n+', '</p><p class="mb-4 leading-relaxed text-gray-800">', cleaned)
    cleaned = '<p class="mb-4 leading-relaxed text-gray-800">' + cleaned + '</p>'
    
    # Final cleanup
    cleaned = re.sub(r'<p[^>]*></p>', '', cleaned)  # Remove empty paragraphs
    cleaned = re.sub(r'(<h[1-6][^>]*>.*?</h[1-6]>)<p[^>]*>', r'\1', cleaned)  # Remove paragraphs after headings
    cleaned = re.sub(r'<p[^>]*>(<h[1-6][^>]*>.*?</h[1-6]>)</p>', r'\1', cleaned)  # Remove paragraphs around headings
    
    return cleaned

app = FastAPI(title="Régulation Marocaine API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import du module principal
try:
    debug_log("SYSTEM STARTUP - Importing Régulation Marocaine modules...")
    from module import (
        TeamGlobal,
        ACAPSSpecialiste,
        AMMCSpecialiste,
        TEAMS
    )
    debug_log("SYSTEM STARTUP - Modules imported successfully")
    
    debug_log("SYSTEM STARTUP - Initializing Régulation Marocaine agents...")
    
    debug_log("AGENT INIT - Team Global initialized", {
        "agent_type": type(TeamGlobal).__name__,
        "agent_initialized": TeamGlobal is not None
    })
    
    debug_log("AGENT INIT - ACAPS Spécialiste initialized", {
        "agent_type": type(ACAPSSpecialiste).__name__,
        "agent_initialized": ACAPSSpecialiste is not None
    })
    
    debug_log("AGENT INIT - AMMC Spécialiste initialized", {
        "agent_type": type(AMMCSpecialiste).__name__,
        "agent_initialized": AMMCSpecialiste is not None
    })
    
    debug_log("SYSTEM STARTUP - All Régulation Marocaine agents initialized successfully! 🎉")
    
except Exception as e:
    debug_log("SYSTEM STARTUP ERROR - Failed to initialize agents", {
        "error_type": type(e).__name__,
        "error_message": str(e)
    })
    TeamGlobal = None
    ACAPSSpecialiste = None
    AMMCSpecialiste = None
    TEAMS = {}

# Stockage en mémoire des sessions
sessions: Dict[str, Dict[str, Any]] = {}

# Modèles Pydantic
class ChatMessage(BaseModel):
    message: str
    team: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    reasoning: str
    timestamp: str
    team_used: str

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_activity: str
    message_count: int
    team_used: str

class WebSocketMessage(BaseModel):
    type: str
    message: Optional[str] = None
    step: Optional[str] = None
    response: Optional[str] = None
    reasoning: Optional[str] = None
    team_used: Optional[str] = None
    timestamp: str

def get_or_create_session(session_id: Optional[str] = None) -> str:
    """Crée ou récupère une session"""
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": [],
            "team_used": "global"
        }
    return session_id

def extract_reasoning_steps_from_agent_logs(reasoning_content: str) -> List[str]:
    """Extrait les vraies étapes de raisonnement depuis les logs de l'agent Agno"""
    if not reasoning_content:
        return []
    
    import re
    steps = []
    
    debug_log("EXTRACTING REASONING STEPS", {
        "content_length": len(reasoning_content),
        "content_preview": reasoning_content[:500] + "..." if len(reasoning_content) > 500 else reasoning_content
    })
    
    # Pattern principal pour capturer les "Reasoning step X" avec tout leur contenu
    reasoning_step_pattern = r'Reasoning step \d+:\s*([^:]+):\s*(.*?)(?=Reasoning step \d+:|$)'
    
    matches = re.findall(reasoning_step_pattern, reasoning_content, re.DOTALL | re.IGNORECASE)
    
    if matches:
        for title, content in matches:
            # Nettoyer le contenu
            clean_content = content.strip()
            if clean_content:
                # Formater comme "Reasoning step X: Titre - Contenu"
                step_text = f"Reasoning step {len(steps) + 1}: {title.strip()}\n\n{clean_content}"
                steps.append(step_text)
        
        debug_log("REASONING STEPS EXTRACTED", {
            "steps_count": len(steps),
            "steps_preview": [step[:200] + "..." if len(step) > 200 else step for step in steps[:3]]
        })
    
    # Si pas de "Reasoning step" trouvés, essayer d'autres patterns
    if not steps:
        # Pattern pour les étapes avec Action/Reasoning/Confidence
        action_pattern = r'Action:\s*(.*?)(?=Reasoning:|Confidence:|$|Action:)'
        reasoning_pattern = r'Reasoning:\s*(.*?)(?=Confidence:|Action:|$)'
        confidence_pattern = r'Confidence:\s*(.*?)(?=Action:|$)'
        
        actions = re.findall(action_pattern, reasoning_content, re.DOTALL | re.IGNORECASE)
        reasonings = re.findall(reasoning_pattern, reasoning_content, re.DOTALL | re.IGNORECASE)
        confidences = re.findall(confidence_pattern, reasoning_content, re.DOTALL | re.IGNORECASE)
        
        # Combiner les éléments
        max_steps = max(len(actions), len(reasonings), len(confidences))
        for i in range(max_steps):
            step_parts = []
            if i < len(actions):
                step_parts.append(f"Action: {actions[i].strip()}")
            if i < len(reasonings):
                step_parts.append(f"Reasoning: {reasonings[i].strip()}")
            if i < len(confidences):
                step_parts.append(f"Confidence: {confidences[i].strip()}")
            
            if step_parts:
                steps.append("\n".join(step_parts))
    
    # Si toujours rien, diviser par paragraphes significatifs
    if not steps:
        paragraphs = [p.strip() for p in reasoning_content.split('\n\n') if p.strip() and len(p) > 50]
        steps = paragraphs[:6]  # Limiter à 6 étapes
    
    debug_log("FINAL REASONING STEPS", {
        "steps_count": len(steps),
        "steps": steps
    })
    
    return steps

def split_reasoning_into_steps(reasoning_content: str) -> List[str]:
    """Divise le reasoning_content en étapes individuelles pour le streaming"""
    return extract_reasoning_steps_from_agent_logs(reasoning_content)

def update_session(session_id: str, message: str, response: str, reasoning: str, team: str):
    """Met à jour une session avec un nouveau message"""
    if session_id in sessions:
        sessions[session_id]["messages"].append({
            "user_message": message,
            "bot_response": response,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        })
        sessions[session_id]["last_activity"] = datetime.now().isoformat()
        sessions[session_id]["team_used"] = team

# Routes
@app.get("/")
def root():
    return {"message": "Régulation Marocaine API", "status": "running"}

@app.get("/health")
async def health_check():
    """Vérifie la santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions_count": len(sessions)
    }

@app.post("/sessions", response_model=dict)
async def create_session():
    """Crée une nouvelle session"""
    session_id = get_or_create_session()
    return {"session_id": session_id}

@app.get("/sessions", response_model=List[SessionInfo])
async def get_sessions():
    """Récupère la liste des sessions"""
    session_list = []
    for session_id, session_data in sessions.items():
        session_list.append(SessionInfo(
            session_id=session_id,
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            message_count=len(session_data["messages"]),
            team_used=session_data["team_used"]
        ))
    
    # Trier par dernière activité
    session_list.sort(key=lambda x: x.last_activity, reverse=True)
    return session_list

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Récupère une session spécifique"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    return {
        "session_id": session_id,
        "session_data": {
            "messages": sessions[session_id]["messages"],
            "created_at": sessions[session_id]["created_at"],
            "last_activity": sessions[session_id]["last_activity"],
            "team_used": sessions[session_id]["team_used"]
        }
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Supprime une session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    del sessions[session_id]
    return {"message": "Session supprimée avec succès"}

@app.post("/chat", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """Envoie un message et retourne une réponse"""
    debug_log("INCOMING REQUEST - Chat Message", {
        "endpoint": "/chat",
        "user_input": chat_message.message,
        "team": chat_message.team
    })
    
    session_id = get_or_create_session(chat_message.session_id)
    
    try:
        # Sélectionner l'agent approprié
        agent = TEAMS.get(chat_message.team, TeamGlobal)
        
        if not agent:
            debug_log("ERROR: Agent not initialized", {"team": chat_message.team})
            return ChatResponse(
                session_id=session_id,
                response="Erreur: Agent non initialisé",
                reasoning="Agent non disponible",
                team_used=chat_message.team
            )
        
        debug_log("PROCESSING REQUEST - Sending to agent...", {
            "agent_type": type(agent).__name__,
            "team": chat_message.team
        })
        
        # Obtenir la réponse de l'agent
        output = agent.run(chat_message.message)
        
        # Extraire le contenu principal
        raw_content = output.content if hasattr(output, 'content') else str(output)
        debug_log("RAW AGENT OUTPUT", {
            "output_type": type(output).__name__,
            "raw_content": raw_content[:500] + "..." if len(raw_content) > 500 else raw_content
        })
        
        # Extraire le reasoning_content si disponible (basé sur l'image)
        reasoning = "Raisonnement non disponible"
        if hasattr(output, "reasoning_content") and output.reasoning_content:
            debug_log("REASONING CONTENT FOUND", {
                "length": len(output.reasoning_content),
                "preview": output.reasoning_content[:200] + "..." if len(output.reasoning_content) > 200 else output.reasoning_content
            })
            reasoning = output.reasoning_content
        else:
            debug_log("REASONING CONTENT NOT FOUND", {
                "has_reasoning_content": hasattr(output, "reasoning_content"),
                "available_attrs": [attr for attr in dir(output) if not attr.startswith('_')]
            })
        
        # Nettoyer le contenu pour l'affichage
        cleaned_response = clean_agent_output(raw_content)
        cleaned_reasoning = clean_agent_output(reasoning) if reasoning != "Raisonnement non disponible" else reasoning
        
        # Mettre à jour la session
        update_session(session_id, chat_message.message, cleaned_response, cleaned_reasoning, chat_message.team)
        
        return ChatResponse(
            session_id=session_id,
            response=cleaned_response,
            reasoning=cleaned_reasoning,
            timestamp=datetime.now().isoformat(),
            team_used=chat_message.team
        )
        
    except Exception as e:
        debug_log("ERROR in Chat", {
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        return ChatResponse(
            session_id=session_id,
            response=f"Erreur: {str(e)}",
            reasoning="Erreur lors du traitement",
            timestamp=datetime.now().isoformat(),
            team_used=chat_message.team
        )

@app.get("/teams")
async def get_teams():
    """Récupère les équipes disponibles"""
    return {
        "teams": ["global", "acaps", "ammc"],
        "agents": ["coordinateur-global", "acaps-specialiste", "ammc-specialiste"]
    }

@app.get("/sessions/{session_id}/export/pdf")
async def export_session_pdf(session_id: str):
    """Exporte une session en PDF"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # TODO: Implémenter l'export PDF avec reportlab
    return {"message": "Export PDF non implémenté - nécessite reportlab"}

# WebSocket pour le chat en temps réel
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket pour le chat en temps réel"""
    try:
        await websocket.accept()
        debug_log("WebSocket connecté", {"session_id": session_id})
        
        while True:
            try:
                # Recevoir le message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Traiter le message
                team = message_data.get("team", "global")
                message = message_data.get("message", "")
                
                # Envoyer le début du raisonnement avec un message dynamique basé sur l'équipe
                team_names = {
                    "global": "Équipe Global",
                    "acaps": "Équipe ACAPS", 
                    "ammc": "Équipe AMMC"
                }
                team_name = team_names.get(team, "Équipe")
                start_message = f"L'{team_name} commence l'analyse de votre demande..."
                
                await websocket.send_text(json.dumps({
                    "type": "reasoning_start",
                    "message": start_message,
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Ne plus envoyer de logs génériques du terminal
                # Le terminal affichera uniquement les reasoning steps
                
                # Obtenir l'agent approprié
                agent = TEAMS.get(team, TeamGlobal)
                
                if agent:
                    # Obtenir la réponse de l'agent
                    output = agent.run(message)
                    raw_content = output.content if hasattr(output, 'content') else str(output)
                    
                    # Extraire le reasoning_content si disponible (basé sur l'image)
                    reasoning_content = ""
                    if hasattr(output, "reasoning_content") and output.reasoning_content:
                        debug_log("WEBSOCKET REASONING CONTENT FOUND", {
                            "length": len(output.reasoning_content),
                            "preview": output.reasoning_content[:200] + "..." if len(output.reasoning_content) > 200 else output.reasoning_content
                        })
                        reasoning_content = output.reasoning_content
                        
                        # Diviser en étapes pour le streaming
                        reasoning_steps = split_reasoning_into_steps(reasoning_content)
                        
                        if reasoning_steps:
                            # Streamer les vraies étapes de raisonnement UNE PAR UNE
                            for i, step in enumerate(reasoning_steps):
                                await websocket.send_text(json.dumps({
                                    "type": "reasoning_step",
                                    "step": step,  # Utiliser directement le contenu de l'agent
                                    "step_number": i + 1,
                                    "total_steps": len(reasoning_steps),
                                    "timestamp": datetime.now().isoformat()
                                }))
                                # Pause pour laisser le temps de lire cette étape
                                import asyncio
                                await asyncio.sleep(10.0)  # 10 secondes pour lire chaque étape
                        else:
                            # Si pas d'étapes détectées, envoyer le contenu complet
                            await websocket.send_text(json.dumps({
                                "type": "reasoning_step",
                                "step": "Raisonnement: " + reasoning_content[:500] + ("..." if len(reasoning_content) > 500 else ""),
                                "timestamp": datetime.now().isoformat()
                            }))
                    else:
                        debug_log("WEBSOCKET REASONING CONTENT NOT FOUND", {
                            "has_reasoning_content": hasattr(output, "reasoning_content")
                        })
                        # Fallback: étapes génériques si pas de reasoning_content
                        reasoning_steps = [
                            "Analyse de la question utilisateur",
                            "Recherche d'informations pertinentes", 
                            "Formulation de la réponse",
                            "Vérification de la cohérence"
                        ]
                        
                        for i, step in enumerate(reasoning_steps):
                            await websocket.send_text(json.dumps({
                                "type": "reasoning_step",
                                "step": step,  # Utiliser directement le contenu de l'agent
                                "step_number": i + 1,
                                "total_steps": len(reasoning_steps),
                                "timestamp": datetime.now().isoformat()
                            }))
                            # Pause pour laisser le temps de lire cette étape
                            import asyncio
                            await asyncio.sleep(10.0)  # 10 secondes pour lire chaque étape
                        
                        reasoning_content = "\n\n".join([f"Étape {i+1}: {step}" for i, step in enumerate(reasoning_steps)])
                    
                    # Nettoyer les contenus
                    cleaned_response = clean_agent_output(raw_content)
                    cleaned_reasoning = clean_agent_output(reasoning_content) if reasoning_content else "Raisonnement non disponible"
                    
                    # Délai très long avant l'envoi de la réponse finale pour laisser le temps de voir les étapes
                    import asyncio
                    await asyncio.sleep(15.0)
                    
                    # Envoyer la réponse finale (sans reasoning pour éviter la duplication)
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "response": cleaned_response,
                        "reasoning": "",  # Pas de reasoning dans la réponse finale
                        "team_used": team,
                        "timestamp": datetime.now().isoformat()
                    }))
                    
                    # Mettre à jour la session
                    update_session(session_id, message, cleaned_response, cleaned_reasoning, team)
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Agent non disponible",
                        "timestamp": datetime.now().isoformat()
                    }))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Format de message invalide",
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "message": f"Erreur: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        debug_log("WebSocket déconnecté", {"session_id": session_id})
    except Exception as e:
        debug_log("Erreur WebSocket", {"error": str(e)})

# Test des agents
@app.get("/api/test-agents")
def test_agents_status():
    """Test si tous les agents sont initialisés"""
    try:
        agent_status = {
            "team_global": {
                "initialized": TeamGlobal is not None,
                "type": type(TeamGlobal).__name__ if TeamGlobal else "None"
            },
            "acaps_specialiste": {
                "initialized": ACAPSSpecialiste is not None,
                "type": type(ACAPSSpecialiste).__name__ if ACAPSSpecialiste else "None"
            },
            "ammc_specialiste": {
                "initialized": AMMCSpecialiste is not None,
                "type": type(AMMCSpecialiste).__name__ if AMMCSpecialiste else "None"
            }
        }
        return {"success": True, "agents": agent_status}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    debug_log("SERVER STARTUP - Starting Régulation Marocaine Server on port 8000...")
    debug_log("SERVER READY - Régulation Marocaine API is now available at http://localhost:8000")
    debug_log("DEBUGGING ENABLED - All agent interactions will be logged to console")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)