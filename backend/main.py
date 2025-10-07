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
    
    # Fix professional document sections
    def format_professional_sections(content):
        # Pattern pour les sections professionnelles (titre en gras suivi de contenu)
        section_pattern = r'^([A-Z][^:]+:)\s*(.*?)(?=^[A-Z][^:]+:|$)'
        
        def replace_section(match):
            title = match.group(1).strip()
            content_text = match.group(2).strip()
            
            # Mapping des titres vers des classes CSS
            title_classes = {
                "Contexte Opérationnel et Impact sur les Activités Bancaires:": "bg-blue-50 border-blue-200 text-blue-900",
                "Procédures, Délais et Documents Requis:": "bg-green-50 border-green-200 text-green-900",
                "Sanctions en Cas de Non-Conformité:": "bg-red-50 border-red-200 text-red-900",
                "Références Réglementaires Utilisées:": "bg-yellow-50 border-yellow-200 text-yellow-900",
                "Références réglementaires exactes:": "bg-yellow-50 border-yellow-200 text-yellow-900"
            }
            
            classes = title_classes.get(title, "bg-gray-50 border-gray-200 text-gray-900")
            
            return f'''
            <div class="border-l-4 {classes} p-4 mb-6 rounded-r-lg">
                <h3 class="text-lg font-semibold mb-3">{title}</h3>
                <div class="text-gray-800 leading-relaxed">
                    {content_text}
                </div>
            </div>
            '''
        
        # Appliquer le formatage aux sections
        content = re.sub(section_pattern, replace_section, content, flags=re.MULTILINE | re.DOTALL)
        return content
    
    # Apply professional sections formatting
    cleaned = format_professional_sections(cleaned)
    
    # Fix emoji sections (📘, ⚙️, 🚨, 📊, 🧩, 📚)
    def replace_emoji_section(match):
        emoji = match.group(1)
        title = match.group(2).strip()
        content = match.group(3).strip()
        
        # Mapping des emojis vers des classes CSS
        emoji_classes = {
            "📘": "bg-blue-50 border-blue-200 text-blue-900",
            "⚙️": "bg-gray-50 border-gray-200 text-gray-900", 
            "🚨": "bg-red-50 border-red-200 text-red-900",
            "📊": "bg-green-50 border-green-200 text-green-900",
            "🧩": "bg-purple-50 border-purple-200 text-purple-900",
            "📚": "bg-yellow-50 border-yellow-200 text-yellow-900"
        }
        
        classes = emoji_classes.get(emoji, "bg-gray-50 border-gray-200 text-gray-900")
        
        return f'''
        <div class="border-l-4 {classes} p-4 mb-6 rounded-r-lg">
            <h3 class="text-lg font-semibold mb-3 flex items-center">
                <span class="text-2xl mr-3">{emoji}</span>
                {title}
            </h3>
            <div class="text-gray-800 leading-relaxed">
                {content}
            </div>
        </div>
        '''
    
    # Pattern pour capturer les sections avec emojis
    emoji_pattern = r'(📘|⚙️|🚨|📊|🧩|📚)\s*([^:]+):\s*(.*?)(?=(?:📘|⚙️|🚨|📊|🧩|📚)\s*[^:]+:|$)'
    cleaned = re.sub(emoji_pattern, replace_emoji_section, cleaned, flags=re.DOTALL)
    
    # Fix bullet points and lists - improved handling
    def fix_lists_in_content(content):
        # Fix bullet points
        content = re.sub(r'^[-*+]\s+(.*?)$', r'<li class="mb-2 ml-4 list-disc">\1</li>', content, flags=re.MULTILINE)
        # Fix numbered lists
        content = re.sub(r'^\d+\.\s+(.*?)$', r'<li class="mb-2 ml-4 list-decimal">\1</li>', content, flags=re.MULTILINE)
        
        # Group consecutive list items
        content = re.sub(r'(<li[^>]*>.*?</li>(?:\s*<li[^>]*>.*?</li>)*)', 
                        lambda m: f'<ul class="mb-4 ml-4 list-disc space-y-1">{m.group(1)}</ul>', 
                        content, flags=re.DOTALL)
        
        return content
    
    # Apply list fixing to the cleaned content
    cleaned = fix_lists_in_content(cleaned)
    
    # Fix regulatory references formatting
    def format_regulatory_references(content):
        # Pattern pour capturer les références réglementaires avec extraits
        ref_pattern = r'(\*\*Document :\*\*.*?)(?=\*\*Document :\*\*|$)'
        
        def format_single_reference(match):
            ref_content = match.group(1).strip()
            
            # Extraire les éléments
            doc_match = re.search(r'\*\*Document :\*\*\s*(.*?)(?=\*\*|$)', ref_content)
            article_match = re.search(r'\*\*Article :\*\*\s*(.*?)(?=\*\*|$)', ref_content)
            extract_match = re.search(r'\*\*Extrait cité :\*\*\s*["\'](.*?)["\']', ref_content)
            date_match = re.search(r'\*\*Date :\*\*\s*(.*?)(?=\*\*|$)', ref_content)
            
            if not doc_match:
                return ref_content  # Return as-is if not properly formatted
            
            doc_name = doc_match.group(1).strip()
            article = article_match.group(1).strip() if article_match else "Non spécifié"
            extract = extract_match.group(1).strip() if extract_match else "Extrait non disponible"
            date = date_match.group(1).strip() if date_match else "Date non spécifiée"
            
            return f'''
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4 rounded-r-lg">
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0">
                        <span class="text-yellow-600 text-lg">📚</span>
                    </div>
                    <div class="flex-1">
                        <h4 class="font-semibold text-yellow-900 mb-2">{doc_name}</h4>
                        <div class="space-y-2 text-sm">
                            <div><span class="font-medium text-yellow-800">Article :</span> <span class="text-yellow-700">{article}</span></div>
                            <div><span class="font-medium text-yellow-800">Date :</span> <span class="text-yellow-700">{date}</span></div>
                            <div class="mt-3">
                                <span class="font-medium text-yellow-800">Extrait cité :</span>
                                <blockquote class="mt-2 p-3 bg-yellow-100 border-l-2 border-yellow-300 italic text-yellow-800">
                                    "{extract}"
                                </blockquote>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
        
        # Appliquer le formatage aux références
        content = re.sub(ref_pattern, format_single_reference, content, flags=re.DOTALL)
        return content
    
    # Apply regulatory references formatting
    cleaned = format_regulatory_references(cleaned)
    
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
        SeniorTradeManager,
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
    
    debug_log("AGENT INIT - Senior Trade Manager initialized", {
        "agent_type": type(SeniorTradeManager).__name__,
        "agent_initialized": SeniorTradeManager is not None
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
    SeniorTradeManager = None
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

def orchestrate_global_to_trade_manager_workflow(user_input: str):
    """
    Orchestre le workflow : User Input → TeamGlobal → SeniorTradeManager → Output final
    """
    debug_log("WORKFLOW START - Orchestrating Global → Trade Manager workflow", {
        "user_input": user_input[:200] + "..." if len(user_input) > 200 else user_input
    })
    
    try:
        # Étape 1: TeamGlobal analyse la question
        debug_log("WORKFLOW STEP 1 - TeamGlobal processing...")
        global_output = TeamGlobal.run(user_input)
        global_content = global_output.content if hasattr(global_output, 'content') else str(global_output)
        global_reasoning = global_output.reasoning_content if hasattr(global_output, 'reasoning_content') else ""
        
        debug_log("WORKFLOW STEP 1 COMPLETE - TeamGlobal output", {
            "content_length": len(global_content),
            "reasoning_length": len(global_reasoning),
            "content_preview": global_content[:300] + "..." if len(global_content) > 300 else global_content,
            "full_content": global_content,  # Log complet pour debug
            "has_references": "Références réglementaires" in global_content,
            "references_section": global_content.split("Références réglementaires")[-1][:500] if "Références réglementaires" in global_content else "Aucune référence trouvée"
        })
        
        # Étape 2: SeniorTradeManager transforme l'output de TeamGlobal
        debug_log("WORKFLOW STEP 2 - SeniorTradeManager processing...")
        
        # Créer le prompt pour SeniorTradeManager pour réécrire l'output de TeamGlobal
        trade_manager_prompt = f"""
        **QUESTION ORIGINALE DE L'UTILISATEUR :**
        {user_input}

        **ANALYSE RÉGLEMENTAIRE FOURNIE PAR L'ÉQUIPE ACAPS & AMMC :**
        {global_content}

        **VOTRE MISSION :**
        En tant que Senior Trade Manager d'une banque marocaine, réécrivez cette analyse réglementaire de manière très métier et professionnelle.

        **VOTRE APPROCHE :**
        - Transformez le langage technique en langage professionnel bancaire
        - Adaptez le contenu aux préoccupations d'un Senior Trade Manager
        - Maintenez la rigueur des références réglementaires
        - Rendez l'information directement utilisable en opérations

        **RÈGLES DE RÉÉCRITURE :**
        - Utilisez un français professionnel bancaire
        - Précisez les implications opérationnelles concrètes
        - Mentionnez les procédures, délais et documents requis
        - Indiquez les sanctions en cas de non-conformité
        - **CONSERVEZ TOUTES LES RÉFÉRENCES RÉGLEMENTAIRES** de l'analyse originale
        - **RÉÉCRIVEZ les références** dans le format standard :
          * **Document :** [Nom exact du document]
          * **Article :** [Numéro d'article/paragraphe]
          * **Extrait cité :** "[Texte exact entre guillemets]"
          * **Date :** [Date de publication]
        - Adaptez le niveau de détail selon la complexité du sujet
        - Ne pas inventer de réglementations ou donner d'avis juridiques contraignants

        **OBJECTIF :** Produire une version professionnelle et métier de cette analyse réglementaire, adaptée aux besoins d'un Senior Trade Manager.
        """
        
        trade_manager_output = SeniorTradeManager.run(trade_manager_prompt)
        final_content = trade_manager_output.content if hasattr(trade_manager_output, 'content') else str(trade_manager_output)
        final_reasoning = trade_manager_output.reasoning_content if hasattr(trade_manager_output, 'reasoning_content') else ""
        
        debug_log("WORKFLOW STEP 2 COMPLETE - SeniorTradeManager output", {
            "content_length": len(final_content),
            "reasoning_length": len(final_reasoning),
            "content_preview": final_content[:300] + "..." if len(final_content) > 300 else final_content
        })
        
        # Combiner les reasoning des deux agents
        combined_reasoning = f"""
        **Étape 1 - Analyse réglementaire (Team Global):**
        {global_reasoning if global_reasoning else "Raisonnement non disponible"}
        
        **Étape 2 - Transformation business (Senior Trade Manager):**
        {final_reasoning if final_reasoning else "Raisonnement non disponible"}
        """
        
        debug_log("WORKFLOW COMPLETE - Final output ready", {
            "final_content_length": len(final_content),
            "combined_reasoning_length": len(combined_reasoning)
        })
        
        return {
            "content": final_content,
            "reasoning": combined_reasoning,
            "workflow_completed": True
        }
        
    except Exception as e:
        debug_log("WORKFLOW ERROR - Orchestration failed", {
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        return {
            "content": f"Erreur dans le workflow: {str(e)}",
            "reasoning": "Erreur lors de l'orchestration des agents",
            "workflow_completed": False
        }

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
        # Utiliser le workflow orchestré : TeamGlobal → SeniorTradeManager
        debug_log("PROCESSING REQUEST - Using orchestrated workflow", {
            "team": chat_message.team,
            "workflow": "TeamGlobal → SeniorTradeManager"
        })
        
        # Orchestrer le workflow
        workflow_result = orchestrate_global_to_trade_manager_workflow(chat_message.message)
        
        if not workflow_result["workflow_completed"]:
            debug_log("WORKFLOW FAILED - Using fallback", {
                "error": workflow_result["content"]
            })
            return ChatResponse(
                session_id=session_id,
                response=workflow_result["content"],
                reasoning=workflow_result["reasoning"],
                timestamp=datetime.now().isoformat(),
                team_used=chat_message.team
            )
        
        # Nettoyer le contenu pour l'affichage
        cleaned_response = clean_agent_output(workflow_result["content"])
        cleaned_reasoning = clean_agent_output(workflow_result["reasoning"])
        
        debug_log("WORKFLOW SUCCESS - Final response ready", {
            "response_length": len(cleaned_response),
            "reasoning_length": len(cleaned_reasoning)
        })
        
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
                
                # Utiliser le workflow orchestré : TeamGlobal → SeniorTradeManager
                debug_log("WEBSOCKET WORKFLOW - Using orchestrated workflow", {
                    "team": team,
                    "workflow": "TeamGlobal → SeniorTradeManager"
                })
                
                # Orchestrer le workflow
                workflow_result = orchestrate_global_to_trade_manager_workflow(message)
                
                if not workflow_result["workflow_completed"]:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": workflow_result["content"],
                        "timestamp": datetime.now().isoformat()
                    }))
                    return
                
                # Diviser le reasoning en étapes pour le streaming
                reasoning_steps = split_reasoning_into_steps(workflow_result["reasoning"])
                        
                if reasoning_steps:
                    # Streamer les étapes de raisonnement
                    for i, step in enumerate(reasoning_steps):
                        await websocket.send_text(json.dumps({
                            "type": "reasoning_step",
                            "step": step,
                            "step_number": i + 1,
                            "total_steps": len(reasoning_steps),
                            "timestamp": datetime.now().isoformat()
                        }))
                        # Pause pour laisser le temps de lire cette étape
                        import asyncio
                        await asyncio.sleep(8.0)  # 8 secondes pour lire chaque étape
                else:
                    # Fallback: étapes génériques du workflow
                    workflow_steps = [
                        "Étape 1: Analyse réglementaire par Team Global",
                        "Étape 2: Transformation en insights business par Senior Trade Manager",
                        "Étape 3: Finalisation de la réponse structurée"
                    ]
                    
                    for i, step in enumerate(workflow_steps):
                        await websocket.send_text(json.dumps({
                            "type": "reasoning_step",
                            "step": step,
                            "step_number": i + 1,
                            "total_steps": len(workflow_steps),
                            "timestamp": datetime.now().isoformat()
                        }))
                        import asyncio
                        await asyncio.sleep(8.0)
                
                # Nettoyer le contenu pour l'affichage
                cleaned_response = clean_agent_output(workflow_result["content"])
                cleaned_reasoning = clean_agent_output(workflow_result["reasoning"])
                
                # Délai avant l'envoi de la réponse finale
                import asyncio
                await asyncio.sleep(10.0)
                    
                # Envoyer la réponse finale
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "response": cleaned_response,
                    "reasoning": "",  # Pas de reasoning dans la réponse finale
                    "team_used": team,
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Mettre à jour la session
                update_session(session_id, message, cleaned_response, cleaned_reasoning, team)
                
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