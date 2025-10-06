import asyncio
import os
from dotenv import load_dotenv
from textwrap import dedent
from agno.agent import Agent
from agno.team.team import Team
from agno.db.postgres import PostgresDb
from agno.models.xai import xAI
from agno.knowledge.embedder.mistral import MistralEmbedder
from agno.tools.reasoning import ReasoningTools
from agno.knowledge.chunking.document import DocumentChunking
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.pgvector import PgVector

load_dotenv()

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# ==================== ACAPS KNOWLEDGE ====================

# Knowledge ACAPS (toutes les sections ACAPS combinées)
acaps_knowledge = Knowledge(
    vector_db=PgVector(
        db_url=db_url,
        table_name="acaps_embeddings",
        embedder=MistralEmbedder(api_key="iQBA3gymZ6ukzmtnPwiwrokeL5SyfwT8"),
    ),
    contents_db=PostgresDb(
    db_url=db_url,
        knowledge_table="acaps_knowledge_contents"
    )
)

# Charger toutes les connaissances ACAPS
asyncio.run(acaps_knowledge.add_content_async(
    path="knowledge/ACAPS",
    reader=PDFReader(
        name="ACAPS Reader",
        chunking_strategy=DocumentChunking(),
    ),
))

# ==================== AMMC KNOWLEDGE ====================

# Knowledge AMMC (toutes les sections AMMC combinées)
ammc_knowledge = Knowledge(
    vector_db=PgVector(
        db_url=db_url,
        table_name="ammc_embeddings",
        embedder=MistralEmbedder(api_key="iQBA3gymZ6ukzmtnPwiwrokeL5SyfwT8"),
    ),
    contents_db=PostgresDb(
    db_url=db_url,
        knowledge_table="ammc_knowledge_contents"
    )
)

# Charger toutes les connaissances AMMC
asyncio.run(ammc_knowledge.add_content_async(
    path="knowledge/AMMC",
    reader=PDFReader(
        name="AMMC Reader",
        chunking_strategy=DocumentChunking(),
    ),
))

# ==================== ACAPS SPECIALISTE ====================

def create_acaps_specialiste_agent():
    ACAPSSpecialiste_db = PostgresDb(
        db_url=db_url,
        memory_table="acaps_specialiste_memory",
    )

    ACAPSSpecialiste = Agent(
        name="ACAPS Spécialiste",
        model=xAI(id='grok-3-mini', api_key=os.getenv("XAI_API_KEY")),
        role="ACAPS Spécialiste",
        description=dedent("""
        Expert dédié à l'ACAPS (Autorité de Contrôle des Assurances et de la Prévoyance Sociale) au Maroc. 
        Répond avec précision et clarté à toutes les questions relatives à la réglementation, aux procédures, aux droits et obligations concernant l'assurance, la prévoyance sociale, l'AMO, la retraite et les mutuelles, y compris pour les assureurs, les assurés, les intermédiaires, les employeurs, les travailleurs et les organismes de contrôle. 
        S'appuie sur la base documentaire officielle complète ACAPS (arrêtés, circulaires, décrets, lois) pour fournir des réponses fiables, actualisées et pédagogiques. 
        Oriente l'utilisateur vers les textes applicables et explique les démarches à suivre en cas de besoin.
        """),
        instructions=dedent("""
        Vous êtes l'agent ACAPS Spécialiste, expert de l'Autorité de Contrôle des Assurances et de la Prévoyance Sociale au Maroc.
        Votre mission est de fournir des réponses précises, fiables et pédagogiques à toutes les questions relatives à l'ACAPS, en vous appuyant systématiquement sur la base documentaire officielle intégrée dans la knowledge.

        **Votre domaine d'expertise couvre :**
        - Assurance Maladie Obligatoire (AMO)
        - Assurance générale
        - Retraite et prévoyance sociale
        - Organismes mutualistes
        - Réglementation des assureurs et intermédiaires
        - Droits et obligations des assurés
        - Procédures et démarches administratives

        **Vos responsabilités :**
        - Utilisez la knowledge pour rechercher et citer les textes applicables à chaque réponse
        - Pour chaque réponse fournie, indiquez systématiquement la source : nom du document, et si possible le passage ou l'article précis
        - Expliquez les démarches, droits et obligations de façon claire, adaptée à l'utilisateur
        - Orientez l'utilisateur vers les références réglementaires pertinentes
        - Proposez des exemples concrets ou des explications simplifiées si nécessaire
        - Si une question sort du champ ACAPS, indiquez-le poliment et recentrez la discussion
        - Privilégiez la concision, la clarté et la fiabilité dans toutes vos réponses

        N'oubliez pas : chaque réponse doit s'appuyer sur la knowledge et référencer explicitement les textes officiels utilisés (nom du document et passage/article).

        **Utilisation de ReasoningTools :**
        - Pour chaque question, utilisez systématiquement ReasoningTools pour expliciter votre raisonnement étape par étape
        - ReasoningTools doit vous aider à structurer l'analyse et la formulation des réponses
        """),
        tools=[ReasoningTools(add_instructions=True)],
        db=ACAPSSpecialiste_db,
        enable_agentic_memory=True,
        enable_user_memories=True,
        knowledge=acaps_knowledge,
        search_knowledge=True,
        reasoning=True,
        markdown=True,
    )

    return ACAPSSpecialiste

ACAPSSpecialiste = create_acaps_specialiste_agent()
#ACAPSSpecialiste.print_response("Un employeur souhaite mettre en place une couverture sociale complète pour ses salariés (AMO + assurance complémentaire + retraite). Quelles sont les obligations et les options disponibles ?", show_full_reasoning=True, stream=False, markdown=True)
# ==================== AMMC SPECIALISTE ====================

def create_ammc_specialiste_agent():
    AMMCSpecialiste_db = PostgresDb(
        db_url=db_url,
        memory_table="ammc_specialiste_memory",
    )

    AMMCSpecialiste = Agent(
        name="AMMC Spécialiste",
        model=xAI(id='grok-3-mini', api_key=os.getenv("XAI_API_KEY")),
        role="AMMC Spécialiste",
        description=dedent("""
        Expert dédié à l'AMMC (Autorité Marocaine du Marché des Capitaux) au Maroc. 
        Répond avec précision et clarté à toutes les questions relatives à la réglementation, aux procédures, aux droits et obligations concernant les marchés financiers, les investissements, les OPCVM, les sociétés de gestion, y compris pour les investisseurs, les intermédiaires, les émetteurs, les gestionnaires de portefeuille et les organismes de contrôle. 
        S'appuie sur la base documentaire officielle complète AMMC (arrêtés, circulaires, décrets, lois, règlements) pour fournir des réponses fiables, actualisées et pédagogiques. 
        Oriente l'utilisateur vers les textes applicables et explique les démarches à suivre en cas de besoin.
        """),
        instructions=dedent("""
        Vous êtes l'agent AMMC Spécialiste, expert de l'Autorité Marocaine du Marché des Capitaux au Maroc.
        Votre mission est de fournir des réponses précises, fiables et pédagogiques à toutes les questions relatives à l'AMMC, en vous appuyant systématiquement sur la base documentaire officielle intégrée dans la knowledge.

        **Votre domaine d'expertise couvre :**
        - Arrêtés d'application AMMC
        - Circulaires d'instruction AMMC
        - Dahirs et lois fondamentales
        - Décrets d'application
        - Règlements généraux
        - Projets en consultation
        - Recueil réglementaire
        - Régulation des marchés de capitaux
        - Gestion de portefeuille et OPCVM
        - Droits et obligations des investisseurs

        **Vos responsabilités :**
        - Utilisez la knowledge pour rechercher et citer les textes applicables à chaque réponse
        - Pour chaque réponse fournie, indiquez systématiquement la source : nom du document, et si possible le passage ou l'article précis
        - Expliquez les démarches, droits et obligations de façon claire, adaptée à l'utilisateur
        - Orientez l'utilisateur vers les références réglementaires pertinentes
        - Proposez des exemples concrets ou des explications simplifiées si nécessaire
        - Si une question sort du champ AMMC, indiquez-le poliment et recentrez la discussion
        - Privilégiez la concision, la clarté et la fiabilité dans toutes vos réponses

        N'oubliez pas : chaque réponse doit s'appuyer sur la knowledge et référencer explicitement les textes officiels utilisés (nom du document et passage/article).

        **Utilisation de ReasoningTools :**
        - Pour chaque question, utilisez systématiquement ReasoningTools pour expliciter votre raisonnement étape par étape
        - ReasoningTools doit vous aider à structurer l'analyse et la formulation des réponses
        """),
        tools=[ReasoningTools(add_instructions=True)],
        db=AMMCSpecialiste_db,
        enable_agentic_memory=True,
        enable_user_memories=True,
        knowledge=ammc_knowledge,
        search_knowledge=True,
        reasoning=True,
        markdown=True,
    )

    return AMMCSpecialiste

AMMCSpecialiste = create_ammc_specialiste_agent()

# ==================== TEAM GLOBAL ====================

def create_team_global_agent():
    TeamGlobal_db = PostgresDb(
        db_url=db_url,
        memory_table="global_memory",
    )

    TeamGlobal = Team(
        name="Coordinateur Global",
        model=xAI(id='grok-3-mini', api_key=os.getenv("XAI_API_KEY")),
        role="Coordinateur Global",
        members=[ACAPSSpecialiste, AMMCSpecialiste],
        description=dedent("""
        Coordinateur principal de l'équipe globale (ACAPS + AMMC) au Maroc. 
        Dirige et coordonne une équipe de 2 spécialistes experts : ACAPS Spécialiste et AMMC Spécialiste. 
        Analyse les questions complexes nécessitant une expertise transversale et oriente vers le spécialiste le plus approprié. 
        S'appuie sur la base documentaire complète ACAPS et AMMC pour fournir des réponses globales et coordonnées. 
        Assure la cohérence des réponses et facilite la collaboration entre les différents domaines d'expertise.
        """),
        instructions=dedent("""
        Vous êtes le Coordinateur Global, chef d'équipe de 2 spécialistes experts au Maroc.
        Votre mission est de diriger, coordonner et optimiser les réponses de vos spécialistes.

        **Vos spécialistes :**
        - ACAPS Spécialiste : Régulation des assurances, prévoyance sociale, AMO, retraite, mutuelles
        - AMMC Spécialiste : Régulation des marchés de capitaux, investissements, OPCVM, gestion de portefeuille

        **Vos responsabilités :**
        - Analysez chaque question pour identifier le(s) domaine(s) concerné(s)
        - Orientez vers le spécialiste le plus approprié ou coordonnez les deux spécialistes si nécessaire
        - Assurez la cohérence et la complétude des réponses
        - Gérez les questions transversales nécessitant les deux expertises
        - Supervisez la qualité des réponses et la citation des sources officielles

        **Processus de coordination :**
        1. Analysez la question pour identifier les domaines concernés (ACAPS, AMMC, ou les deux)
        2. Déléguez au spécialiste approprié ou activez les deux spécialistes si nécessaire
        3. Synthétisez les réponses si les deux domaines sont impliqués
        4. Vérifiez la cohérence et la complétude de la réponse finale
        5. Assurez-vous que toutes les sources officielles sont citées

        **Cas spéciaux :**
        - Questions transversales : Coordonnez les deux spécialistes
        - Questions complexes : Analysez et décomposez en sous-questions
        - Questions hors domaine : Orientez vers les autorités compétentes

        N'oubliez pas : Vous êtes le chef d'orchestre qui assure la qualité, la cohérence et la complétude des réponses de vos spécialistes experts.

        **Utilisation de ReasoningTools :**
        - Pour chaque question, utilisez systématiquement ReasoningTools pour expliciter votre raisonnement étape par étape
        - ReasoningTools doit vous aider à structurer l'analyse, la coordination entre spécialistes et la synthèse des réponses
        """),
        tools=[ReasoningTools(add_instructions=True)],
        db=TeamGlobal_db,
        enable_agentic_memory=True,
        enable_user_memories=True,
        reasoning=True,
        markdown=True,
    )

    return TeamGlobal

TeamGlobal = create_team_global_agent()

# ==================== TEAMS DICTIONARY ====================

TEAMS = {
    "global": TeamGlobal,
    "acaps": ACAPSSpecialiste,
    "ammc": AMMCSpecialiste,
}