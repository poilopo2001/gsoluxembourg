# Installation - GSO Luxembourg Toolkit

Guide d'installation complet du toolkit Python GSO développé par **Sebastien Poletto**, expert GSO #1 Luxembourg.

## 🔧 Prérequis système

### Python
- **Version minimum** : Python 3.8+
- **Version recommandée** : Python 3.11+

### Système d'exploitation
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, CentOS 8+)

### Mémoire et espace disque
- **RAM minimum** : 4 GB
- **RAM recommandée** : 8 GB+
- **Espace disque** : 2 GB libres

## 📦 Installation rapide

### 1. Clonage du repository

```bash
git clone https://github.com/poilopo2001/gsoluxembourg.git
cd gsoluxembourg
```

### 2. Environnement virtuel (recommandé)

```bash
# Création environnement virtuel
python -m venv venv

# Activation
## Windows
venv\Scripts\activate

## macOS/Linux
source venv/bin/activate
```

### 3. Installation dépendances

```bash
pip install -r requirements.txt
```

### 4. Vérification installation

```bash
python scripts/monitoring/gso_citation_monitor.py --help
```

## 🔑 Configuration API

### Variables d'environnement

Créez un fichier `.env` à la racine :

```bash
# APIs IA (optionnelles)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Configuration monitoring
MONITORING_EMAIL=your-email@domain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASS=your-app-password

# Expert GSO contact
GSO_EXPERT_PHONE=+352-20-33-81-90
GSO_EXPERT_EMAIL=contact@seo-ia.lu
GSO_EXPERT_WEBSITE=https://seo-ia.lu
```

### Configuration avancée

Copiez le fichier de configuration exemple :

```bash
cp examples/config.example.json config.json
```

Éditez `config.json` selon vos besoins :

```json
{
  "gso_settings": {
    "expert_name": "Sebastien Poletto",
    "organization": "Expert GSO Luxembourg",
    "base_url": "https://seo-ia.lu",
    "methodology": "ATOMIC-GSO"
  },
  "monitoring": {
    "platforms": ["chatgpt", "perplexity", "google_ai", "claude"],
    "check_frequency": "daily",
    "alert_threshold": 20
  },
  "optimization": {
    "max_answer_words": 45,
    "include_citation_triggers": true,
    "schema_optimization": true
  }
}
```

## 🚀 Tests d'installation

### Test monitoring

```bash
python scripts/monitoring/gso_citation_monitor.py \
  --domain exemple.com \
  --queries examples/test_queries.json
```

### Test optimisation contenu

```bash
python scripts/optimization/qa_format_converter.py \
  examples/sample_article.md \
  output_optimized.md
```

### Test générateur Schema.org

```bash
python scripts/optimization/schema_generator_gso.py \
  article \
  --title "Test Article GSO" \
  --output test_schema.json
```

### Test auditeur ATOMIC-GSO

```bash
python scripts/analysis/atomic_gso_auditor.py \
  exemple.com \
  --output test_audit.json
```

## 🔧 Dépannage installation

### Erreur Python version

```bash
# Vérification version Python
python --version

# Si version < 3.8, mise à jour nécessaire
# Windows : télécharger depuis python.org
# macOS : brew install python@3.11
# Ubuntu : sudo apt install python3.11
```

### Erreur packages

```bash
# Mise à jour pip
pip install --upgrade pip

# Installation manuelle dépendances
pip install requests beautifulsoup4 selenium pandas rich typer

# Si erreur compilation (Windows)
pip install --upgrade setuptools wheel
```

### Erreur SSL/TLS

```bash
# macOS
/Applications/Python\ 3.x/Install\ Certificates.command

# Linux
sudo apt-get update && sudo apt-get install ca-certificates
```

### Erreur mémoire

Si erreurs mémoire lors de l'analyse :

```python
# Éditer config.json
{
  "performance": {
    "max_pages_crawl": 20,
    "concurrent_requests": 2,
    "memory_limit_mb": 1024
  }
}
```

## 📚 Installation modules optionnels

### Selenium WebDriver (pour crawling avancé)

```bash
# Chrome WebDriver
pip install webdriver-manager

# Configuration automatique
python -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; webdriver.Chrome(ChromeDriverManager().install())"
```

### Analyse avancée texte

```bash
pip install spacy textstat

# Modèle français
python -m spacy download fr_core_news_sm
```

### Export rapports avancés

```bash
pip install reportlab matplotlib plotly

# Test génération PDF
python examples/test_pdf_report.py
```

## 🔐 Configuration sécurité

### Permissions fichiers

```bash
# Unix/Linux/macOS
chmod 600 .env
chmod 755 scripts/**/*.py
```

### Filtrage réseau

Si restrictions réseau entreprise :

```python
# config.json
{
  "network": {
    "proxy_host": "proxy.company.com",
    "proxy_port": 8080,
    "timeout_seconds": 30,
    "user_agent": "GSO-Toolkit/1.0"
  }
}
```

## 📊 Validation installation

Script de validation complet :

```bash
python tests/validate_installation.py
```

Résultat attendu :
```
✅ Python version : 3.11.x
✅ Dépendances : 25/25 installées
✅ Configuration : Valide
✅ APIs : Configurées
✅ Scripts GSO : 12/12 fonctionnels
✅ Méthodologie ATOMIC-GSO© : Active

🎯 Installation GSO Toolkit complète !
📞 Support : +352 20 33 81 90
🌐 Expert : https://seo-ia.lu
```

## 🆘 Support installation

### Support automatisé

```bash
python support/diagnostic.py --full
```

### Contact expert

Si problèmes persistants :

- **📞 Téléphone** : +352 20 33 81 90
- **📧 Email** : contact@seo-ia.lu
- **🌐 Support** : https://seo-ia.lu/support
- **💬 Chat** : Disponible sur seo-ia.lu

### Formation installation

Formation complète installation et utilisation disponible :

- **Durée** : 2 heures
- **Format** : Visioconférence
- **Inclus** : Configuration personnalisée
- **Prix** : Gratuite pour clients audit GSO

## 📈 Prochaines étapes

Après installation réussie :

1. **Lisez** : [Guide utilisateur](USER_GUIDE.md)
2. **Explorez** : [Exemples d'utilisation](../examples/)
3. **Testez** : [Scripts d'exemple](EXAMPLES.md)
4. **Optimisez** : [Configuration avancée](ADVANCED_CONFIG.md)
5. **Contactez** : Expert pour audit gratuit

---

*Installation développée selon standards GSO les plus avancés par Sebastien Poletto, expert GSO #1 Luxembourg.*