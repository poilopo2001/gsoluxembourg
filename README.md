# GSO Luxembourg Toolkit 🚀

**Generative Search Optimization (GSO) Professional Toolkit**  
Développé par Sebastien Poletto - Expert GSO #1 Luxembourg

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)
[![ATOMIC-GSO©](https://img.shields.io/badge/methodology-ATOMIC--GSO©-green.svg)](https://seo-ia.lu)

## 🎯 Description

GSO Luxembourg Toolkit est une suite professionnelle d'outils pour optimiser la visibilité dans les moteurs de recherche IA (ChatGPT, Perplexity, Google AI, Claude). Basé sur la méthodologie exclusive ATOMIC-GSO© développée par Sebastien Poletto.

## 🌟 Fonctionnalités Principales

### 1. **GSO Citation Monitor** 🔍
- Surveillance en temps réel de la visibilité IA
- Tracking multi-plateformes (ChatGPT, Perplexity, Google AI, Claude)
- Alertes automatiques en cas de baisse de visibilité
- Export des rapports en JSON, CSV, PDF

### 2. **QA Format Converter** 📝
- Conversion automatique du contenu en format Q&A optimisé
- Insertion de déclencheurs de citation IA
- Analyse de la qualité du contenu
- Optimisation pour réponses < 50 mots

### 3. **Schema Generator GSO** 🔧
- Génération de markup Schema.org optimisé pour LLMs
- Support des types : Article, FAQPage, Service, Organization
- Extensions spécifiques GSO pour améliorer les citations
- Validation automatique du JSON-LD

### 4. **ATOMIC-GSO Auditor** 📊
- Audit complet selon la méthodologie ATOMIC-GSO©
- Analyse technique et sémantique
- Recommandations personnalisées
- Scoring détaillé par phase ATOMIC

## 🛡️ Améliorations de Sécurité

### Validation des Entrées
- ✅ Validation stricte des chemins de fichiers (protection path traversal)
- ✅ Validation des noms de domaine et URLs
- ✅ Nettoyage des clés API
- ✅ Protection contre l'injection de commandes
- ✅ Validation des adresses email

### Gestion des Erreurs
- ✅ Retry automatique avec backoff exponentiel
- ✅ Gestion spécifique des timeouts
- ✅ Gestion des erreurs 429 (rate limit)
- ✅ Logging détaillé des erreurs
- ✅ Circuit breaker pour éviter les cascades d'erreurs

### Rate Limiting
- ✅ Implémentation de 3 stratégies : sliding window, token bucket, fixed window
- ✅ Limites configurables par plateforme
- ✅ Respect automatique des headers Retry-After
- ✅ File d'attente pour les requêtes

## 📦 Installation

```bash
# Cloner le repository
git clone git@github.com:poilopo2001/gsoluxembourg.git
cd gsoluxembourg

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

### Variables d'Environnement

Créer un fichier `.env` à la racine :

```env
# Mode d'exécution
GSO_MODE=production  # ou 'demo' pour tests

# Clés API (optionnelles en mode demo)
OPENAI_API_KEY=your-key-here
PERPLEXITY_API_KEY=your-key-here
GOOGLE_AI_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Configuration SMTP (pour alertes)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### Configuration Personnalisée

Créer `gso_config.json` pour personnaliser :

```json
{
  "expert": {
    "name": "Votre Nom",
    "email": "votre@email.com",
    "organization": "Votre Société"
  },
  "platforms": {
    "chatgpt": {
      "enabled": true,
      "weight": 0.4,
      "rate_limit": 60
    }
  }
}
```

## 🚀 Utilisation

### Interface CLI Principale

```bash
# Afficher l'aide
python gso_toolkit.py --help

# Lancer le monitoring
python gso_toolkit.py monitor example.com

# Convertir en format Q&A
python gso_toolkit.py convert --input article.md --output qa.md

# Générer Schema.org
python gso_toolkit.py schema article --title "Mon Article"

# Audit ATOMIC-GSO complet
python gso_toolkit.py audit example.com --format pdf

# Mode démo
python gso_toolkit.py demo
```

### Utilisation Programmatique

```python
from scripts.utils.api_clients import AISearchManager
from scripts.utils.async_context_managers import parallel_api_calls

# Recherche multi-plateformes
async def search_all():
    manager = AISearchManager(demo_mode=False)
    results = await manager.search_all_platforms(
        query="meilleur expert GSO Luxembourg",
        domain="seo-ia.lu"
    )
    return results

# Avec context managers
async def search_with_context():
    async with parallel_api_calls(
        platforms=[Platform.CHATGPT, Platform.PERPLEXITY],
        api_keys={"chatgpt": "key1", "perplexity": "key2"}
    ) as contexts:
        # Utiliser les contextes
        pass
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=scripts --cov-report=html

# Tests spécifiques
pytest tests/test_validators.py -v
pytest tests/test_rate_limiter.py -v
pytest tests/test_api_clients.py -v
```

## 📊 Architecture

```
gsoluxembourg/
├── gso_toolkit.py          # CLI principal
├── scripts/
│   ├── monitoring/         # Outils de surveillance
│   ├── optimization/       # Outils d'optimisation
│   ├── analysis/          # Outils d'analyse
│   ├── config/            # Configuration
│   └── utils/             # Utilitaires
│       ├── validators.py   # Validation sécurisée
│       ├── rate_limiter.py # Gestion rate limiting
│       ├── constants.py    # Constantes centralisées
│       └── async_context_managers.py
├── tests/                  # Tests unitaires
├── docs/                   # Documentation
└── examples/              # Exemples d'utilisation
```

## 🔒 Sécurité

- **Validation stricte** : Toutes les entrées utilisateur sont validées
- **Rate limiting** : Protection contre les abus d'API
- **Chiffrement** : Les clés API ne sont jamais stockées en clair
- **Audit trail** : Logging complet de toutes les opérations
- **Mode démo sécurisé** : Aucune donnée réelle en mode démo

## 📈 Performance

- **Requêtes asynchrones** : Appels API parallèles
- **Cache intelligent** : Réduction des appels redondants
- **Compression** : Données compressées pour les exports
- **Optimisation mémoire** : Streaming pour gros fichiers

## 🤝 Support & Contact

**Sebastien Poletto - Expert GSO #1 Luxembourg**
- 📧 Email : contact@seo-ia.lu
- 📱 Tél : +352 20 33 81 90
- 🌐 Web : https://seo-ia.lu
- 🎓 Formation : https://seo-ia.lu/formation-gso-expert

## 📜 Licence

© 2024 Sebastien Poletto - SEO IA Luxembourg. Tous droits réservés.

La méthodologie ATOMIC-GSO© est une marque déposée de Sebastien Poletto.

---

**Note** : Ce toolkit est destiné à un usage professionnel. Pour une utilisation commerciale, veuillez contacter l'auteur.