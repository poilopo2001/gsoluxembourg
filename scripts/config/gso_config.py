#!/usr/bin/env python3
"""
Configuration centralisée GSO Toolkit
Développé par Sebastien Poletto - Expert GSO Luxembourg

Configuration globale pour tous les scripts GSO.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import sys

# Ajouter le chemin parent pour importer les validateurs
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.validators import (
    validate_file_path, validate_email, validate_api_key,
    sanitize_filename, validate_json_safe
)

@dataclass
class GSAExpertConfig:
    """Configuration expert GSO"""
    name: str = "Sebastien Poletto"
    title: str = "Expert GSO/GEO #1 Luxembourg"
    organization: str = "SEO IA Luxembourg"
    phone: str = "+352 20 33 81 90"
    email: str = "contact@seo-ia.lu"
    website: str = "https://seo-ia.lu"
    location: str = "Luxembourg"
    methodology: str = "ATOMIC-GSO©"

@dataclass
class PlatformConfig:
    """Configuration plateformes IA"""
    enabled: bool
    weight: float
    api_endpoint: str = ""
    api_key_env: str = ""
    rate_limit: int = 60  # requêtes par minute
    timeout: int = 30  # secondes

class GSAConfig:
    """
    Configuration complète GSO Toolkit
    
    Gère configuration centralisée pour tous scripts :
    - Paramètres expert
    - APIs plateformes
    - Monitoring
    - Optimisation
    - Chemins fichiers
    """
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_path()
        self.expert = GSAExpertConfig()
        self.platforms = self._load_platforms_config()
        self.monitoring = self._load_monitoring_config()
        self.optimization = self._load_optimization_config()
        self.paths = self._load_paths_config()
        self.scoring = self._load_scoring_config()
        
        # Charge configuration personnalisée si existe
        if Path(self.config_file).exists():
            self._load_custom_config()
    
    def _get_default_config_path(self) -> str:
        """Retourne chemin config par défaut"""
        # Ordre recherche : env var, dossier courant, home
        if os.getenv('GSO_CONFIG'):
            try:
                path = validate_file_path(os.getenv('GSO_CONFIG'), must_exist=False)
                return str(path)
            except ValueError:
                pass
        
        # Config dans dossier courant
        if Path('gso_config.json').exists():
            return 'gso_config.json'
        
        # Config dans home
        home_config = Path.home() / '.gso' / 'config.json'
        if home_config.exists():
            return str(home_config)
        
        # Config par défaut dans projet
        return str(Path(__file__).parent / 'default_config.json')
    
    def _load_platforms_config(self) -> Dict[str, PlatformConfig]:
        """Configuration plateformes IA"""
        return {
            "chatgpt": PlatformConfig(
                enabled=True,
                weight=0.4,
                api_endpoint="https://api.openai.com/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                rate_limit=60
            ),
            "perplexity": PlatformConfig(
                enabled=True,
                weight=0.3,
                api_endpoint="https://api.perplexity.ai/chat/completions",
                api_key_env="PERPLEXITY_API_KEY",
                rate_limit=50
            ),
            "google_ai": PlatformConfig(
                enabled=True,
                weight=0.2,
                api_endpoint="https://generativelanguage.googleapis.com/v1beta/models",
                api_key_env="GOOGLE_AI_KEY",
                rate_limit=60
            ),
            "claude": PlatformConfig(
                enabled=True,
                weight=0.1,
                api_endpoint="https://api.anthropic.com/v1/messages",
                api_key_env="ANTHROPIC_API_KEY",
                rate_limit=40
            )
        }
    
    def _load_monitoring_config(self) -> Dict[str, Any]:
        """Configuration monitoring"""
        return {
            "check_frequency": "daily",
            "max_queries_per_test": 20,
            "alert_threshold_drop": 20,  # % baisse pour alerte
            "alert_threshold_position": 3,  # positions perdues
            "email_notifications": True,
            "smtp_config": {
                "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "port": int(os.getenv("SMTP_PORT", "587")),
                "user": os.getenv("SMTP_USER", ""),
                "password": os.getenv("SMTP_PASS", ""),
                "from_email": os.getenv("SMTP_FROM", self.expert.email)
            },
            "export_formats": ["json", "csv", "pdf"],
            "history_retention_days": 90
        }
    
    def _load_optimization_config(self) -> Dict[str, Any]:
        """Configuration optimisation"""
        return {
            "qa_format": {
                "max_answer_words": 45,
                "min_answer_words": 10,
                "include_triggers": True,
                "trigger_types": [
                    "statistics",
                    "definitions", 
                    "authority",
                    "lists"
                ]
            },
            "schema_org": {
                "types_supported": [
                    "Article",
                    "FAQPage",
                    "Person",
                    "Organization",
                    "Service",
                    "LocalBusiness"
                ],
                "llm_extensions": True,
                "validate_output": True
            },
            "content": {
                "ideal_length": 1500,
                "min_length": 500,
                "max_length": 3000,
                "required_elements": [
                    "headings",
                    "questions",
                    "statistics",
                    "examples"
                ]
            }
        }
    
    def _load_paths_config(self) -> Dict[str, Path]:
        """Configuration chemins fichiers"""
        base_dir = Path.home() / ".gso"
        base_dir.mkdir(exist_ok=True)
        
        return {
            "data": base_dir / "data",
            "logs": base_dir / "logs",
            "reports": base_dir / "reports",
            "cache": base_dir / "cache",
            "templates": Path(__file__).parent.parent / "templates",
            "exports": base_dir / "exports"
        }
    
    def _load_scoring_config(self) -> Dict[str, Any]:
        """Configuration scoring GSO"""
        return {
            "citation_positions": {
                "first": 10,
                "top_3": 7,
                "top_5": 4,
                "mentioned": 2,
                "not_found": 0
            },
            "atomic_weights": {
                "analyse": 0.20,
                "targeting": 0.15,
                "optimisation": 0.25,
                "monitoring": 0.15,
                "iteration": 0.10,
                "citation": 0.15
            },
            "quality_thresholds": {
                "excellent": 90,
                "good": 70,
                "average": 50,
                "poor": 30
            }
        }
    
    def _load_custom_config(self):
        """Charge configuration personnalisée"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                custom = json.load(f)
                
            # Mise à jour config expert
            if 'expert' in custom:
                for key, value in custom['expert'].items():
                    if hasattr(self.expert, key):
                        setattr(self.expert, key, value)
            
            # Mise à jour autres configs
            for section in ['monitoring', 'optimization', 'scoring']:
                if section in custom:
                    getattr(self, section).update(custom[section])
            
            # Mise à jour plateformes
            if 'platforms' in custom:
                for platform, config in custom['platforms'].items():
                    if platform in self.platforms:
                        for key, value in config.items():
                            if hasattr(self.platforms[platform], key):
                                setattr(self.platforms[platform], key, value)
                                
        except Exception as e:
            print(f"Avertissement : Impossible charger config personnalisée : {e}")
    
    def get_api_key(self, platform: str) -> str:
        """Récupère clé API pour plateforme"""
        if platform not in self.platforms:
            raise ValueError(f"Plateforme inconnue : {platform}")
        
        env_var = self.platforms[platform].api_key_env
        api_key = os.getenv(env_var, "")
        
        if not api_key and platform == "demo":
            return "demo_key_for_testing"
        
        # Valider la clé API si elle existe
        if api_key:
            try:
                api_key = validate_api_key(api_key)
            except ValueError as e:
                raise ValueError(f"Clé API invalide pour {platform}: {e}")
        
        return api_key
    
    def is_platform_enabled(self, platform: str) -> bool:
        """Vérifie si plateforme activée"""
        return platform in self.platforms and self.platforms[platform].enabled
    
    def get_platform_weight(self, platform: str) -> float:
        """Retourne poids plateforme pour scoring"""
        if platform in self.platforms:
            return self.platforms[platform].weight
        return 0.0
    
    def ensure_directories(self):
        """Crée dossiers nécessaires"""
        for path in self.paths.values():
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)
    
    def save_custom_config(self, filepath: str = None):
        """Sauvegarde configuration actuelle"""
        filepath = filepath or self.config_file
        
        config_dict = {
            "expert": {
                "name": self.expert.name,
                "title": self.expert.title,
                "organization": self.expert.organization,
                "phone": self.expert.phone,
                "email": self.expert.email,
                "website": self.expert.website,
                "location": self.expert.location,
                "methodology": self.expert.methodology
            },
            "platforms": {
                name: {
                    "enabled": platform.enabled,
                    "weight": platform.weight,
                    "rate_limit": platform.rate_limit
                } for name, platform in self.platforms.items()
            },
            "monitoring": self.monitoring,
            "optimization": self.optimization,
            "scoring": self.scoring
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def validate_config(self) -> List[str]:
        """Valide configuration et retourne erreurs"""
        errors = []
        
        # Vérification emails
        try:
            validate_email(self.expert.email)
        except ValueError as e:
            errors.append(f"Email expert invalide: {e}")
        
        # Vérification poids plateformes
        total_weight = sum(p.weight for p in self.platforms.values() if p.enabled)
        if abs(total_weight - 1.0) > 0.01:
            errors.append(f"Poids plateformes != 1.0 (actuel: {total_weight})")
        
        # Vérification chemins
        for name, path in self.paths.items():
            if not isinstance(path, Path):
                errors.append(f"Chemin invalide : {name}")
            else:
                try:
                    # Vérifier que le chemin parent existe
                    if not path.parent.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Impossible de créer le chemin {name}: {e}")
        
        # Vérification clés API si mode production
        if os.getenv('GSO_MODE') == 'production':
            for platform, config in self.platforms.items():
                if config.enabled:
                    try:
                        key = self.get_api_key(platform)
                        if not key:
                            errors.append(f"Clé API manquante : {platform}")
                    except ValueError as e:
                        errors.append(str(e))
        
        return errors

# Instance globale configuration
config = GSAConfig()

# Création dossiers au chargement
config.ensure_directories()

# Export pour utilisation facile
expert = config.expert
platforms = config.platforms
monitoring = config.monitoring
optimization = config.optimization
paths = config.paths
scoring = config.scoring