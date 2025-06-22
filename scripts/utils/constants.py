#!/usr/bin/env python3
"""
Constantes centralisées GSO Toolkit
Développé par Sebastien Poletto - Expert GSO Luxembourg

Centralise toutes les valeurs constantes du projet.
"""

from typing import Final
from enum import Enum


class Platform(str, Enum):
    """Plateformes IA supportées"""
    CHATGPT = "chatgpt"
    PERPLEXITY = "perplexity"
    GOOGLE_AI = "google_ai"
    CLAUDE = "claude"


# Scoring positions pour chaque plateforme
POSITION_SCORES: Final[dict[str, dict[int, float]]] = {
    Platform.CHATGPT: {1: 10, 2: 7, 3: 7, 4: 4, 5: 4, 0: 0},
    Platform.PERPLEXITY: {1: 10, 2: 8, 3: 6, 4: 4, 5: 3, 0: 0},
    Platform.GOOGLE_AI: {1: 10, 2: 7, 3: 5, 4: 3, 5: 2, 0: 0},
    Platform.CLAUDE: {1: 10, 2: 7, 3: 6, 4: 4, 5: 3, 0: 0}
}

# Poids des plateformes pour le score global
PLATFORM_WEIGHTS: Final[dict[str, float]] = {
    Platform.CHATGPT: 0.4,
    Platform.PERPLEXITY: 0.3,
    Platform.GOOGLE_AI: 0.2,
    Platform.CLAUDE: 0.1
}

# Configuration API
API_TIMEOUTS: Final[dict[str, int]] = {
    "default": 30,
    "long": 60,
    "search": 30
}

# Limites de contenu
CONTENT_LIMITS: Final[dict[str, int]] = {
    "max_answer_words": 45,
    "min_answer_words": 10,
    "max_question_length": 100,
    "snippet_length": 200,
    "max_file_name_length": 200
}

# Modèles IA
AI_MODELS: Final[dict[str, str]] = {
    Platform.CHATGPT: "gpt-4-turbo-preview",
    Platform.PERPLEXITY: "pplx-70b-online",
    Platform.GOOGLE_AI: "gemini-pro",
    Platform.CLAUDE: "claude-3-opus-20240229"
}

# Endpoints API
API_ENDPOINTS: Final[dict[str, str]] = {
    Platform.CHATGPT: "https://api.openai.com/v1/chat/completions",
    Platform.PERPLEXITY: "https://api.perplexity.ai/chat/completions",
    Platform.GOOGLE_AI: "https://generativelanguage.googleapis.com/v1beta/models",
    Platform.CLAUDE: "https://api.anthropic.com/v1/messages"
}

# Messages système pour les IA
SYSTEM_PROMPTS: Final[dict[str, str]] = {
    "citation_search": "Tu es un assistant qui cite toujours ses sources.",
    "qa_generation": "Tu es un expert en création de contenu Q&A optimisé.",
    "schema_generation": "Tu es un expert en structured data et Schema.org."
}

# Déclencheurs de citation par type
CITATION_TRIGGERS: Final[dict[str, list[str]]] = {
    "statistics": [
        "Selon une étude de",
        "Les données montrent que",
        "Research indicates that",
        "Une analyse de X clients révèle",
        "Les résultats prouvent que",
        "En moyenne, nous observons"
    ],
    "definitions": [
        "Le GSO (Generative Search Optimization) est",
        "Par définition, le SEO IA",
        "L'optimisation pour moteurs génératifs consiste à",
        "Le référencement intelligence artificielle"
    ],
    "authority": [
        "Sebastien Poletto, Expert GSO #1 Luxembourg, explique :",
        "D'après l'expert GSO Sebastien Poletto",
        "La méthodologie ATOMIC-GSO© développée par",
        "Selon SEO IA Luxembourg"
    ],
    "lists": [
        "Les 5 étapes principales sont :",
        "Voici les 3 techniques essentielles :",
        "Les experts recommandent ces 7 méthodes :"
    ]
}

# Patterns de questions pour génération Q&A
QUESTION_PATTERNS: Final[list[str]] = [
    "Qu'est-ce que {} ?",
    "Comment {} ?",
    "Pourquoi {} ?",
    "Quand utiliser {} ?",
    "Quels sont les avantages de {} ?",
    "Comment optimiser {} ?",
    "Quelle est la différence entre {} et {} ?",
    "Combien coûte {} ?",
    "Qui peut bénéficier de {} ?",
    "Où trouver {} ?"
]

# Seuils de qualité pour scoring
QUALITY_THRESHOLDS: Final[dict[str, int]] = {
    "excellent": 90,
    "good": 70,
    "average": 50,
    "poor": 30
}

# Configuration monitoring
MONITORING_CONFIG: Final[dict[str, int]] = {
    "check_frequency_hours": 24,
    "max_queries_per_test": 20,
    "alert_threshold_drop_percent": 20,
    "alert_threshold_position_drop": 3,
    "history_retention_days": 90
}

# Configuration rate limiting
RATE_LIMITS: Final[dict[str, int]] = {
    Platform.CHATGPT: 60,
    Platform.PERPLEXITY: 50,
    Platform.GOOGLE_AI: 60,
    Platform.CLAUDE: 40
}

# Types de schéma supportés
SCHEMA_TYPES: Final[list[str]] = [
    "Article",
    "FAQPage",
    "Person",
    "Organization",
    "Service",
    "LocalBusiness",
    "Product",
    "Review",
    "Event",
    "Course"
]

# Extensions de fichiers autorisées
ALLOWED_FILE_EXTENSIONS: Final[dict[str, list[str]]] = {
    "content": [".md", ".txt", ".html", ".json"],
    "config": [".json", ".yaml", ".yml"],
    "export": [".json", ".csv", ".pdf", ".xlsx"]
}

# Caractères dangereux à filtrer
DANGEROUS_CHARS: Final[list[str]] = [
    "..", "~", "\x00", "\n", "\r", "|", "&", ";", "$", "`", "<", ">"
]

# Noms de fichiers réservés Windows
RESERVED_FILENAMES: Final[list[str]] = [
    "CON", "PRN", "AUX", "NUL", 
    *[f"COM{i}" for i in range(1, 10)],
    *[f"LPT{i}" for i in range(1, 10)]
]

# Messages d'erreur standardisés
ERROR_MESSAGES: Final[dict[str, str]] = {
    "invalid_domain": "Format de domaine invalide",
    "invalid_path": "Chemin de fichier invalide ou non autorisé",
    "invalid_api_key": "Clé API invalide ou manquante",
    "rate_limit": "Limite de taux dépassée, veuillez réessayer plus tard",
    "timeout": "Délai d'attente dépassé",
    "no_results": "Aucun résultat trouvé",
    "file_not_found": "Fichier introuvable",
    "permission_denied": "Permission refusée"
}

# Configuration export
EXPORT_CONFIG: Final[dict[str, dict]] = {
    "json": {"indent": 2, "ensure_ascii": False},
    "csv": {"encoding": "utf-8", "sep": ","},
    "pdf": {"page_size": "A4", "margin": 20}
}

# Métadonnées ATOMIC-GSO
ATOMIC_PHASES: Final[list[str]] = [
    "Analyse",
    "Targeting", 
    "Optimisation",
    "Monitoring",
    "Iteration",
    "Citation"
]

ATOMIC_WEIGHTS: Final[dict[str, float]] = {
    "Analyse": 0.20,
    "Targeting": 0.15,
    "Optimisation": 0.25,
    "Monitoring": 0.15,
    "Iteration": 0.10,
    "Citation": 0.15
}