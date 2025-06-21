#!/usr/bin/env python3
"""
Tests unitaires pour QA Format Converter
"""

import pytest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from optimization.qa_format_converter import QAFormatConverter, ContentSection

class TestQAFormatConverter:
    """Tests pour le convertisseur Q&A"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.converter = QAFormatConverter()
    
    def test_extract_main_concept(self):
        """Test extraction concept principal"""
        # Test basique
        assert self.converter._extract_main_concept("Qu'est-ce que le GSO ?") == "gso"
        
        # Test avec mots-outils
        assert self.converter._extract_main_concept("Comment optimiser pour ChatGPT") == "optimiser chatgpt"
        
        # Test cas vide
        assert self.converter._extract_main_concept("") == ""
    
    def test_analyze_content_structure(self):
        """Test analyse structure contenu"""
        content = """
# Titre Principal

Contenu du paragraphe principal.

## Sous-titre 1

Contenu de la section 1.

### Question fréquente ?

Réponse à la question.
"""
        sections = self.converter.analyze_content_structure(content)
        
        assert len(sections) == 3
        assert sections[0].heading == "Titre Principal"
        assert sections[0].level == 1
        assert sections[1].heading == "Sous-titre 1"
        assert sections[1].level == 2
    
    def test_generate_optimized_answer(self):
        """Test génération réponse optimisée"""
        question = "Qu'est-ce que le GSO ?"
        content = "Le GSO (Generative Search Optimization) est une méthodologie d'optimisation pour les moteurs de recherche génératifs comme ChatGPT, Perplexity et Google AI. Cette approche vise à améliorer la visibilité dans les réponses générées par l'IA."
        
        answer = self.converter._generate_optimized_answer(question, content)
        
        # Vérifier longueur < 50 mots
        assert len(answer.split()) <= 50
        
        # Vérifier présence de mots-clés
        assert "GSO" in answer or "Generative Search Optimization" in answer
    
    def test_identify_citation_triggers(self):
        """Test identification déclencheurs citation"""
        answer = "Selon une étude de 2024, le GSO améliore la visibilité de 400%."
        triggers = self.converter._identify_citation_triggers(answer)
        
        assert len(triggers) > 0
        assert any("Selon une étude" in trigger for trigger in triggers)
    
    def test_empty_content_handling(self):
        """Test gestion contenu vide"""
        sections = self.converter.analyze_content_structure("")
        assert len(sections) == 0
    
    def test_malformed_content(self):
        """Test contenu mal formaté"""
        content = "Texte sans structure markdown"
        sections = self.converter.analyze_content_structure(content)
        # Ne doit pas crasher
        assert isinstance(sections, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])