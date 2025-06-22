#!/usr/bin/env python3
"""
Tests unitaires pour le module de configuration
Développé par Sebastien Poletto - Expert GSO Luxembourg
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

# Ajouter le chemin parent pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.config.gso_config import (
    GSAConfig, GSAExpertConfig, PlatformConfig
)


class TestGSAExpertConfig:
    """Tests pour GSAExpertConfig"""
    
    def test_default_values(self):
        """Test valeurs par défaut"""
        expert = GSAExpertConfig()
        
        assert expert.name == "Sebastien Poletto"
        assert expert.title == "Expert GSO/GEO #1 Luxembourg"
        assert expert.organization == "SEO IA Luxembourg"
        assert expert.email == "contact@seo-ia.lu"
        assert expert.methodology == "ATOMIC-GSO©"


class TestPlatformConfig:
    """Tests pour PlatformConfig"""
    
    def test_platform_config_creation(self):
        """Test création config plateforme"""
        config = PlatformConfig(
            enabled=True,
            weight=0.5,
            api_endpoint="https://api.example.com",
            api_key_env="TEST_API_KEY",
            rate_limit=30,
            timeout=60
        )
        
        assert config.enabled
        assert config.weight == 0.5
        assert config.rate_limit == 30
        assert config.timeout == 60


class TestGSAConfig:
    """Tests pour GSAConfig"""
    
    def test_default_initialization(self):
        """Test initialisation par défaut"""
        config = GSAConfig()
        
        # Vérifier expert
        assert config.expert.name == "Sebastien Poletto"
        
        # Vérifier plateformes
        assert "chatgpt" in config.platforms
        assert "perplexity" in config.platforms
        assert "google_ai" in config.platforms
        assert "claude" in config.platforms
        
        # Vérifier poids total
        total_weight = sum(p.weight for p in config.platforms.values() if p.enabled)
        assert abs(total_weight - 1.0) < 0.01
    
    def test_platform_config_values(self):
        """Test valeurs config plateformes"""
        config = GSAConfig()
        
        # ChatGPT
        assert config.platforms["chatgpt"].weight == 0.4
        assert config.platforms["chatgpt"].rate_limit == 60
        
        # Perplexity
        assert config.platforms["perplexity"].weight == 0.3
        assert config.platforms["perplexity"].rate_limit == 50
    
    def test_monitoring_config(self):
        """Test config monitoring"""
        config = GSAConfig()
        
        assert config.monitoring["check_frequency"] == "daily"
        assert config.monitoring["max_queries_per_test"] == 20
        assert config.monitoring["alert_threshold_drop"] == 20
        assert "json" in config.monitoring["export_formats"]
    
    def test_optimization_config(self):
        """Test config optimisation"""
        config = GSAConfig()
        
        assert config.optimization["qa_format"]["max_answer_words"] == 45
        assert "FAQPage" in config.optimization["schema_org"]["types_supported"]
        assert config.optimization["content"]["ideal_length"] == 1500
    
    def test_paths_config(self):
        """Test config chemins"""
        config = GSAConfig()
        
        assert all(isinstance(path, Path) for path in config.paths.values())
        assert config.paths["data"].name == "data"
        assert config.paths["logs"].name == "logs"
    
    def test_scoring_config(self):
        """Test config scoring"""
        config = GSAConfig()
        
        assert config.scoring["citation_positions"]["first"] == 10
        assert config.scoring["atomic_weights"]["optimisation"] == 0.25
        assert config.scoring["quality_thresholds"]["excellent"] == 90
    
    @patch.dict('os.environ', {'GSO_CONFIG': '/tmp/test_config.json'})
    def test_custom_config_path_from_env(self):
        """Test chemin config depuis variable environnement"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"expert": {"name": "Test User"}}, f)
            temp_path = f.name
        
        try:
            with patch.dict('os.environ', {'GSO_CONFIG': temp_path}):
                config = GSAConfig()
                # Le chemin devrait être validé mais le fichier custom chargé
                assert config.expert.name == "Test User"
        finally:
            os.unlink(temp_path)
    
    def test_load_custom_config(self):
        """Test chargement config personnalisée"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_data = {
                "expert": {
                    "name": "Custom Name",
                    "email": "custom@example.com"
                },
                "platforms": {
                    "chatgpt": {
                        "enabled": False,
                        "weight": 0.5
                    }
                },
                "monitoring": {
                    "check_frequency": "hourly"
                }
            }
            json.dump(custom_data, f)
            temp_path = f.name
        
        try:
            config = GSAConfig(config_file=temp_path)
            
            assert config.expert.name == "Custom Name"
            assert config.expert.email == "custom@example.com"
            assert not config.platforms["chatgpt"].enabled
            assert config.platforms["chatgpt"].weight == 0.5
            assert config.monitoring["check_frequency"] == "hourly"
        finally:
            os.unlink(temp_path)
    
    def test_get_api_key(self):
        """Test récupération clés API"""
        config = GSAConfig()
        
        # Test sans clé
        assert config.get_api_key("demo") == "demo_key_for_testing"
        
        # Test avec clé environnement
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123'}):
            key = config.get_api_key("chatgpt")
            assert key == "test-key-123"
        
        # Test plateforme inconnue
        with pytest.raises(ValueError, match="Plateforme inconnue"):
            config.get_api_key("unknown_platform")
        
        # Test clé invalide
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'invalid@key!'}):
            with pytest.raises(ValueError, match="Clé API invalide"):
                config.get_api_key("chatgpt")
    
    def test_is_platform_enabled(self):
        """Test vérification plateforme activée"""
        config = GSAConfig()
        
        assert config.is_platform_enabled("chatgpt")
        assert not config.is_platform_enabled("unknown_platform")
    
    def test_get_platform_weight(self):
        """Test récupération poids plateforme"""
        config = GSAConfig()
        
        assert config.get_platform_weight("chatgpt") == 0.4
        assert config.get_platform_weight("unknown") == 0.0
    
    def test_ensure_directories(self):
        """Test création dossiers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = GSAConfig()
            # Rediriger vers dossier temporaire
            for key in config.paths:
                config.paths[key] = Path(tmpdir) / config.paths[key].name
            
            config.ensure_directories()
            
            # Vérifier que tous les dossiers existent
            for path in config.paths.values():
                assert path.exists()
                assert path.is_dir()
    
    def test_save_custom_config(self):
        """Test sauvegarde configuration"""
        config = GSAConfig()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save_custom_config(temp_path)
            
            # Recharger et vérifier
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["expert"]["name"] == "Sebastien Poletto"
            assert "chatgpt" in saved_data["platforms"]
            assert saved_data["scoring"]["citation_positions"]["first"] == 10
        finally:
            os.unlink(temp_path)
    
    def test_validate_config_success(self):
        """Test validation config réussie"""
        config = GSAConfig()
        errors = config.validate_config()
        
        # Pas d'erreurs avec config par défaut
        assert len(errors) == 0
    
    def test_validate_config_invalid_email(self):
        """Test validation avec email invalide"""
        config = GSAConfig()
        config.expert.email = "invalid-email"
        
        errors = config.validate_config()
        assert any("Email expert invalide" in e for e in errors)
    
    def test_validate_config_invalid_weights(self):
        """Test validation avec poids invalides"""
        config = GSAConfig()
        config.platforms["chatgpt"].weight = 0.8
        # Total maintenant > 1.0
        
        errors = config.validate_config()
        assert any("Poids plateformes != 1.0" in e for e in errors)
    
    @patch.dict('os.environ', {'GSO_MODE': 'production'})
    def test_validate_config_production_mode(self):
        """Test validation en mode production"""
        config = GSAConfig()
        
        # Sans clés API en production
        errors = config.validate_config()
        assert any("Clé API manquante" in e for e in errors)
        
        # Avec clés API valides
        with patch.dict('os.environ', {
            'OPENAI_API_KEY': 'valid-key-123',
            'PERPLEXITY_API_KEY': 'valid-key-456',
            'GOOGLE_AI_KEY': 'valid-key-789',
            'ANTHROPIC_API_KEY': 'valid-key-012'
        }):
            errors = config.validate_config()
            # Pas d'erreurs de clés manquantes
            assert not any("Clé API manquante" in e for e in errors)


class TestConfigIntegration:
    """Tests d'intégration pour la configuration"""
    
    def test_global_config_instance(self):
        """Test instance globale config"""
        from scripts.config.gso_config import config, expert, platforms
        
        assert isinstance(config, GSAConfig)
        assert isinstance(expert, GSAExpertConfig)
        assert isinstance(platforms, dict)
        assert all(isinstance(p, PlatformConfig) for p in platforms.values())
    
    def test_config_modification_persistence(self):
        """Test persistance modifications config"""
        config = GSAConfig()
        
        # Modifier config
        original_name = config.expert.name
        config.expert.name = "Modified Name"
        
        # Sauvegarder
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save_custom_config(temp_path)
            
            # Recharger
            new_config = GSAConfig(config_file=temp_path)
            assert new_config.expert.name == "Modified Name"
        finally:
            os.unlink(temp_path)
            config.expert.name = original_name  # Restaurer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])