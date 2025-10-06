# 📚 Documentation du Module Agno V2 - Équipe de Régulation Marocaine Simplifiée

## 🎯 Vue d'ensemble

Le module `module.py` implémente une architecture simplifiée d'équipe Agno composée de **3 agents spécialisés** pour répondre aux questions des professionnels des banques et assurances marocaines.

### 🏗️ Architecture Simplifiée

```
Team Global (Coordinateur Global)
├── ACAPS Spécialiste
│   └── Expertise complète ACAPS (AMO + Assurance + Retraite + Mutuelle)
└── AMMC Spécialiste
    └── Expertise complète AMMC (Arrêtés + Circulaires + Dahirs + Décrets + Règlements + Projets + Recueil)
```

## 🔧 Configuration Technique

### Base de données
- **URL** : `postgresql+psycopg://ai:ai@localhost:5532/ai`
- **Extension** : pgvector pour les embeddings
- **Embedder** : MistralEmbedder (dimensions: 1024)

### Modèle IA
- **Modèle** : xAI Grok-3-mini
- **API Key** : Variable d'environnement `XAI_API_KEY`

## 🏛️ ACAPS SPÉCIALISTE

### Base de Connaissance
- **Base de données** : `acaps_embeddings`
- **Documents** : `knowledge/ACAPS/` (toutes les sections ACAPS combinées)
- **Table mémoire** : `acaps_specialiste_memory`

### Expertise Complète
L'agent ACAPS Spécialiste combine l'expertise de 4 domaines :

#### 1. Assurance Maladie Obligatoire (AMO)
- Réglementation AMO au Maroc
- Droits et obligations des travailleurs indépendants
- Procédures pour les salariés et employeurs
- Gestion des organismes gestionnaires

#### 2. Assurance Générale
- Assurance générale au Maroc
- Réglementation pour assureurs et assurés
- Droits des intermédiaires
- Contrôle des organismes

#### 3. Retraite et Prévoyance Sociale
- Retraite et prévoyance sociale
- Droits des retraités et travailleurs
- Obligations des employeurs
- Contrôle des organismes

#### 4. Organismes Mutualistes
- Organismes mutualistes au Maroc
- Réglementation des mutuelles
- Droits des assurés
- Contrôle des organismes

### Instructions Spécialisées
- Réponses précises basées sur la base documentaire officielle ACAPS
- Citation systématique des sources (arrêtés, circulaires, décrets, lois)
- Explications adaptées selon le profil utilisateur
- Orientation vers les textes applicables
- Utilisation de ReasoningTools pour structurer le raisonnement

## 🏛️ AMMC SPÉCIALISTE

### Base de Connaissance
- **Base de données** : `ammc_embeddings`
- **Documents** : `knowledge/AMMC/` (toutes les sections AMMC combinées)
- **Table mémoire** : `ammc_specialiste_memory`

### Expertise Complète
L'agent AMMC Spécialiste combine l'expertise de 7 domaines :

#### 1. Arrêtés AMMC
- Arrêtés réglementaires AMMC
- Marchés financiers marocains
- Droits des investisseurs
- Obligations des intermédiaires

#### 2. Circulaires AMMC
- Circulaires d'instruction AMMC
- Procédures réglementaires
- Droits des émetteurs
- Contrôle des organismes

#### 3. Dahirs et Lois AMMC
- Dahirs et lois fondamentales
- Cadre légal des marchés financiers
- Droits fondamentaux
- Obligations légales

#### 4. Décrets AMMC
- Décrets d'application AMMC
- Procédures d'application
- Droits des acteurs
- Obligations réglementaires

#### 5. Règlements Généraux AMMC
- Règlements généraux AMMC
- Cadre réglementaire général
- Droits et obligations générales
- Procédures générales

#### 6. Projets en Consultation AMMC
- Projets en consultation AMMC
- Évolutions réglementaires
- Droits des parties prenantes
- Processus de consultation

#### 7. Recueil AMMC
- Recueil réglementaire AMMC
- Documentation complète
- Droits et obligations
- Références réglementaires

### Instructions Spécialisées
- Réponses précises basées sur la base documentaire officielle AMMC
- Citation systématique des sources (arrêtés, circulaires, décrets, lois, règlements)
- Explications adaptées selon le profil utilisateur
- Orientation vers les textes applicables
- Utilisation de ReasoningTools pour structurer le raisonnement

## 🌐 COORDINATEUR GLOBAL

### Configuration
- **Table mémoire** : `global_memory`
- **Équipes** : ACAPS Spécialiste + AMMC Spécialiste

### Responsabilités
- Coordination des 2 spécialistes
- Analyse des questions transversales
- Orientation vers le spécialiste approprié
- Synthèse des réponses globales
- Supervision de la cohérence générale

### Processus de Coordination
1. **Analyse** : Identifier le(s) domaine(s) concerné(s) (ACAPS, AMMC, ou les deux)
2. **Délégation** : Orienter vers le spécialiste approprié ou activer les deux spécialistes
3. **Synthèse** : Combiner les réponses si les deux domaines sont impliqués
4. **Vérification** : Assurer la cohérence et la complétude de la réponse finale
5. **Citation** : Vérifier que toutes les sources officielles sont citées

### Cas Spéciaux
- **Questions transversales** : Coordonne les deux spécialistes
- **Questions complexes** : Analyse et décompose en sous-questions
- **Questions hors domaine** : Oriente vers les autorités compétentes

## 🔄 Workflow de Traitement

### 1. Réception de la Question
- Le Coordinateur Global analyse la question
- Identification des domaines concernés (ACAPS/AMMC)

### 2. Orientation
- Délégation vers le spécialiste approprié
- Activation du coordinateur global si nécessaire

### 3. Traitement Spécialisé
- Le spécialiste analyse la question
- Recherche dans la base de connaissance appropriée
- Génération de la réponse avec reasoning steps
- Citation des sources officielles

### 4. Synthèse (si nécessaire)
- Vérification de la cohérence
- Combinaison des réponses transversales
- Formatage en markdown
- Retour au coordinateur global

## 📊 Bases de Données

### Tables d'Embeddings
- `acaps_embeddings` (toutes les sections ACAPS combinées)
- `ammc_embeddings` (toutes les sections AMMC combinées)

### Tables de Contenu
- `acaps_knowledge_contents`
- `ammc_knowledge_contents`

### Tables de Mémoire
- `acaps_specialiste_memory`
- `ammc_specialiste_memory`
- `global_memory`

## 🚀 Utilisation

### Initialisation
```python
# Le module se charge automatiquement au démarrage
# Toutes les bases de connaissance sont créées
# Tous les agents sont initialisés
```

### Accès aux Agents
```python
# Accès direct aux agents
from module import TEAMS

# Team Global (recommandé pour les questions transversales)
global_team = TEAMS["global"]

# ACAPS Spécialiste (questions assurance/prévoyance)
acaps_agent = TEAMS["acaps"]

# AMMC Spécialiste (questions marchés financiers)
ammc_agent = TEAMS["ammc"]
```

### Test d'Exemple
```python
# Test avec une question transversale
TeamGlobal.print_response(
    "Un investisseur souhaite créer une société d'assurance et une société de gestion de portefeuille au Maroc. Quelles sont les réglementations applicables ?",
    show_full_reasoning=True,
    stream=True,
    markdown=True
)
```

## 🎯 Avantages de l'Architecture Simplifiée

### 1. Simplicité
- Architecture claire avec 3 agents seulement
- Maintenance facilitée
- Déploiement simplifié

### 2. Efficacité
- Agents spécialisés avec expertise complète
- Pas de délégation complexe entre multiples agents
- Réponses directes et rapides

### 3. Flexibilité
- Questions transversales gérées par le Coordinateur Global
- Questions spécialisées traitées directement par les spécialistes
- Adaptation facile aux besoins

### 4. Performance
- Recherche sémantique optimisée sur des bases consolidées
- Mémoire persistante pour chaque spécialiste
- Traitement en streaming avec reasoning steps

## 🔧 Maintenance

### Mise à jour des Bases de Connaissance
- Ajout de nouveaux documents dans `knowledge/ACAPS/` ou `knowledge/AMMC/`
- Mise à jour automatique des embeddings
- Synchronisation des contenus

### Surveillance des Performances
- Monitoring des réponses des spécialistes
- Analyse de la qualité des reasoning steps
- Optimisation des processus de coordination

### Évolution des Agents
- Mise à jour des instructions spécialisées
- Amélioration des descriptions d'expertise
- Adaptation aux nouveaux besoins réglementaires

## 📝 Notes Techniques

### Embeddings
- **Modèle** : MistralEmbedder
- **Dimensions** : 1024
- **API Key** : Intégrée dans le code

### Chunking
- **Stratégie** : DocumentChunking
- **Taille** : Optimisée pour la recherche sémantique

### Mémoire
- **Type** : PostgreSQL
- **Persistance** : Activée pour tous les agents
- **Synchronisation** : Automatique

### Formatage
- **Output** : Markdown
- **Streaming** : Activé
- **Reasoning** : Complet avec étapes structurées

### Reasoning Steps
- **Structure** : Action/Reasoning/Confidence
- **Streaming** : Affichage étape par étape
- **Format** : "Reasoning step X: Titre" + contenu détaillé

## 🔄 Intégration avec le Frontend

### WebSocket Communication
- **Types de messages** : `reasoning_start`, `reasoning_step`, `response`
- **Streaming** : Étapes de raisonnement en temps réel
- **Remplacement** : Chaque étape remplace la précédente

### API REST
- **Endpoints** : `/chat`, `/sessions`, `/teams`
- **Fallback** : Utilisé si WebSocket non disponible
- **Sessions** : Gestion persistante des conversations

## 🎯 Cas d'Usage

### Questions ACAPS
- Obligations AMO pour les employeurs
- Procédures d'assurance complémentaire
- Droits des retraités
- Réglementation des mutuelles

### Questions AMMC
- Création de société de gestion
- Réglementation des OPCVM
- Obligations des intermédiaires
- Droits des investisseurs

### Questions Transversales
- Création d'entreprise multi-secteurs
- Réglementations croisées
- Procédures complexes
- Coordination entre autorités

## 📈 Métriques de Performance

### Temps de Réponse
- **Questions simples** : < 5 secondes
- **Questions complexes** : < 15 secondes
- **Questions transversales** : < 30 secondes

### Qualité des Réponses
- **Précision** : Basée sur la documentation officielle
- **Cohérence** : Vérifiée par le Coordinateur Global
- **Complétude** : Sources citées systématiquement

### Expérience Utilisateur
- **Streaming** : Étapes de raisonnement visibles
- **Progression** : Indicateur (X/Y) des étapes
- **Transparence** : Processus de raisonnement exposé

---

*Cette documentation décrit l'architecture simplifiée du module Agno V2 pour les régulations marocaines, permettant aux professionnels des banques et assurances d'obtenir des réponses précises et fiables basées sur la documentation officielle avec un système de reasoning steps en streaming.*
