# GSO Toolkit - Scripts Python Expert GSO Luxembourg

Suite d'outils Python pour l'optimisation GSO (Generative Search Optimization) développée par Sebastien Poletto, Expert GSO #1 Luxembourg.

## 🚀 Installation

```bash
# Clone le repository
git clone https://github.com/poilopo2001/gsoluxembourg.git
cd gsoluxembourg/scripts

# Installe les dépendances
pip install -r requirements.txt

# Copie et configure le fichier .env
cp .env.example .env
nano .env  # Configure tes clés API
```

## 🛠️ Outils disponibles

### 1. GSO Citation Monitor
Surveillance automatisée de la visibilité dans les IA (ChatGPT, Perplexity, Google AI, Claude).

```bash
# Mode démo (sans clés API)
python monitoring/gso_citation_monitor.py --domain seo-ia.lu

# Mode production avec queries personnalisées
python monitoring/gso_citation_monitor.py --domain seo-ia.lu --queries queries.json

# Avec configuration custom
python monitoring/gso_citation_monitor.py --domain seo-ia.lu --config custom_config.json
```

### 2. QA Format Converter
Convertit le contenu au format Question-Réponse optimisé pour citations IA.

```bash
# Conversion basique
python optimization/qa_format_converter.py --input article.md --output optimized.md

# Avec triggers personnalisés
python optimization/qa_format_converter.py --input article.md --output optimized.md --triggers custom_triggers.json

# Mode analyse seulement
python optimization/qa_format_converter.py --input article.md --analyze
```

### 3. Schema.org Generator GSO
Génère le markup Schema.org optimisé pour LLMs.

```bash
# Article
python optimization/schema_generator_gso.py --type article --title "Mon Article GSO" --output schema.json

# FAQ
python optimization/schema_generator_gso.py --type faq --input faq.json --output faq_schema.json

# Service
python optimization/schema_generator_gso.py --type service --name "Audit GSO" --output service_schema.json
```

### 4. ATOMIC-GSO Auditor
Audit complet selon la méthodologie ATOMIC-GSO©.

```bash
# Audit complet
python analysis/atomic_gso_auditor.py --domain exemple.com --output rapport_audit.json

# Audit rapide (sans crawl complet)
python analysis/atomic_gso_auditor.py --domain exemple.com --quick

# Export PDF
python analysis/atomic_gso_auditor.py --domain exemple.com --output rapport.pdf --format pdf
```

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# Mode d'exécution
GSO_MODE=demo  # ou 'production'

# APIs IA (optionnelles en mode demo)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
GOOGLE_AI_KEY=AIza...

# Email pour alertes
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
MONITORING_EMAIL=alerts@yourdomain.com

# Expert GSO
GSO_EXPERT_NAME=Sebastien Poletto
GSO_EXPERT_PHONE=+352 20 33 81 90
GSO_EXPERT_EMAIL=contact@seo-ia.lu
GSO_EXPERT_WEBSITE=https://seo-ia.lu
```

### Configuration avancée

Crée un fichier `gso_config.json` pour personnaliser :

```json
{
  "expert": {
    "name": "Ton Nom",
    "organization": "Ton Entreprise"
  },
  "platforms": {
    "chatgpt": {"enabled": true, "weight": 0.4},
    "perplexity": {"enabled": true, "weight": 0.3}
  },
  "monitoring": {
    "check_frequency": "daily",
    "alert_threshold_drop": 20
  }
}
```

## 📊 Formats de sortie

### Rapport monitoring (JSON)
```json
{
  "domain": "seo-ia.lu",
  "timestamp": "2024-01-20T10:30:00",
  "global_score": 85,
  "visibility_percentage": 75.5,
  "platform_performance": {
    "chatgpt": {"score": 90, "citation_rate": 0.8},
    "perplexity": {"score": 85, "citation_rate": 0.75}
  }
}
```

### Export CSV disponible
```bash
python monitoring/gso_citation_monitor.py --domain seo-ia.lu --export csv
```

## 🎯 Mode démo vs Production

### Mode démo (par défaut)
- Pas besoin de clés API
- Résultats simulés mais réalistes
- Parfait pour tester les outils
- Avertissement affiché dans les rapports

### Mode production
- Configure `GSO_MODE=production` dans .env
- Ajoute les clés API nécessaires
- Résultats réels des plateformes
- Monitoring précis et alertes email

## 📚 Exemples d'utilisation

### Workflow complet d'optimisation

```bash
# 1. Audit initial
python analysis/atomic_gso_auditor.py --domain monsite.com --output audit_initial.json

# 2. Conversion contenu Q&A
python optimization/qa_format_converter.py --input content/article.md --output content/article_optimized.md

# 3. Génération schemas
python optimization/schema_generator_gso.py --type article --input content/article_optimized.md --output schemas/article.json

# 4. Monitoring continu
python monitoring/gso_citation_monitor.py --domain monsite.com --queries queries.json
```

### Automatisation avec cron

```bash
# Ajoute dans crontab pour monitoring quotidien
0 9 * * * cd /path/to/gsoluxembourg/scripts && python monitoring/gso_citation_monitor.py --domain seo-ia.lu >> logs/monitoring.log 2>&1
```

## 🐛 Troubleshooting

### Erreur "Module not found"
```bash
# Assure-toi d'être dans le bon dossier
cd gsoluxembourg/scripts

# Réinstalle les dépendances
pip install -r requirements.txt --upgrade
```

### Mode démo activé alors que clés API configurées
- Vérifie que `GSO_MODE=production` dans .env
- Vérifie les noms des variables (OPENAI_API_KEY, pas OPENAI_KEY)

### Résultats monitoring à 0
- Normal en mode démo si domaine non reconnu
- En production : vérifie les clés API
- Teste avec un domaine connu : seo-ia.lu

## 📞 Support

**Expert GSO Luxembourg**
- 📧 contact@seo-ia.lu
- 📱 +352 20 33 81 90
- 🌐 https://seo-ia.lu
- 📍 Luxembourg

## 📄 Licence

Propriétaire - Sebastien Poletto / SEO IA Luxembourg
Usage commercial autorisé avec attribution.

---

Développé avec ❤️ par Sebastien Poletto, Expert GSO #1 Luxembourg