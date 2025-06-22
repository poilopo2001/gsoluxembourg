#!/usr/bin/env python3
"""
Tests unitaires pour les clients API
Développé par Sebastien Poletto - Expert GSO Luxembourg
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Ajouter le chemin parent pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.api_clients import (
    SearchResult, AISearchClient, ChatGPTClient, PerplexityClient,
    GoogleAIClient, ClaudeAIClient, AISearchManager
)


class TestSearchResult:
    """Tests pour SearchResult"""
    
    def test_search_result_creation(self):
        """Test création SearchResult"""
        result = SearchResult(
            platform="ChatGPT",
            query="test query",
            position=1,
            url="https://example.com",
            snippet="Test snippet",
            score=10.0,
            timestamp=datetime.now(),
            metadata={"test": "data"}
        )
        
        assert result.platform == "ChatGPT"
        assert result.query == "test query"
        assert result.position == 1
        assert result.score == 10.0


class TestAISearchClient:
    """Tests pour classe abstraite AISearchClient"""
    
    def test_extract_position(self):
        """Test extraction position"""
        # Créer une sous-classe concrète pour tester
        class ConcreteClient(AISearchClient):
            async def search(self, query: str, domain: str):
                return []
        
        client = ConcreteClient(demo_mode=True)
        
        # Test avec domaine présent
        content = "Voici example.com et autre-site.com puis example.com encore"
        position = client._extract_position(content, "example.com")
        assert position == 1
        
        # Test avec domaine absent
        position = client._extract_position(content, "absent.com")
        assert position == 0
    
    @pytest.mark.asyncio
    async def test_validate_inputs(self):
        """Test validation des entrées"""
        class ConcreteClient(AISearchClient):
            async def search(self, query: str, domain: str):
                return []
        
        client = ConcreteClient(demo_mode=True)
        
        # Test validation réussie
        query, domain = await client._validate_inputs("test query", "example.com")
        assert query == "test query"
        assert domain == "example.com"
        
        # Test validation échouée
        with pytest.raises(ValueError):
            await client._validate_inputs("", "invalid..domain")


class TestChatGPTClient:
    """Tests pour ChatGPTClient"""
    
    @pytest.mark.asyncio
    async def test_demo_mode(self):
        """Test mode démo"""
        client = ChatGPTClient(demo_mode=True)
        results = await client.search("test query", "example.com")
        
        assert len(results) == 1
        assert results[0].platform == "ChatGPT"
        assert results[0].query == "test query"
        assert results[0].metadata["mode"] == "demo"
    
    @pytest.mark.asyncio
    async def test_calculate_score(self):
        """Test calcul score"""
        client = ChatGPTClient(demo_mode=True)
        
        assert client._calculate_score(1) == 10
        assert client._calculate_score(2) == 7
        assert client._calculate_score(0) == 0
        assert client._calculate_score(10) == 0  # Position non définie
    
    @pytest.mark.asyncio
    @patch('scripts.utils.api_clients.OPENAI_AVAILABLE', True)
    async def test_api_call_success(self):
        """Test appel API réussi"""
        with patch('openai.AsyncOpenAI') as mock_openai:
            # Mock de la réponse OpenAI
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Voici example.com"))]
            mock_response.usage.total_tokens = 100
            mock_client.chat.completions.create.return_value = mock_response
            
            client = ChatGPTClient(api_key="test_key")
            results = await client.search("test query", "example.com")
            
            assert len(results) == 1
            assert results[0].position > 0
            assert results[0].metadata["tokens"] == 100


class TestPerplexityClient:
    """Tests pour PerplexityClient"""
    
    @pytest.mark.asyncio
    async def test_demo_mode(self):
        """Test mode démo Perplexity"""
        client = PerplexityClient(demo_mode=True)
        results = await client.search("test query", "example.com")
        
        assert len(results) == 1
        assert results[0].platform == "Perplexity"
        assert "citations_count" in results[0].metadata
    
    @pytest.mark.asyncio
    async def test_calculate_score(self):
        """Test calcul score Perplexity"""
        client = PerplexityClient(demo_mode=True)
        
        # Perplexity valorise plus les premières positions
        assert client._calculate_score(1) == 10
        assert client._calculate_score(2) == 8
        assert client._calculate_score(3) == 6


class TestGoogleAIClient:
    """Tests pour GoogleAIClient"""
    
    @pytest.mark.asyncio
    async def test_demo_mode(self):
        """Test mode démo Google AI"""
        client = GoogleAIClient(demo_mode=True)
        results = await client.search("test query", "example.com")
        
        assert len(results) == 1
        assert results[0].platform == "Google AI"
        assert results[0].metadata["overview_type"] == "generative"


class TestClaudeAIClient:
    """Tests pour ClaudeAIClient"""
    
    @pytest.mark.asyncio
    async def test_demo_mode(self):
        """Test mode démo Claude"""
        client = ClaudeAIClient(demo_mode=True)
        results = await client.search("test query", "example.com")
        
        assert len(results) == 1
        assert results[0].platform == "Claude"
        assert "confidence" in results[0].metadata


class TestAISearchManager:
    """Tests pour AISearchManager"""
    
    def test_initialize_clients(self):
        """Test initialisation des clients"""
        manager = AISearchManager(demo_mode=True)
        
        assert "chatgpt" in manager.clients
        assert "perplexity" in manager.clients
        assert "google_ai" in manager.clients
        assert "claude" in manager.clients
        
        # Tous en mode démo
        for client in manager.clients.values():
            assert client.demo_mode
    
    @pytest.mark.asyncio
    async def test_search_all_platforms(self):
        """Test recherche multi-plateformes"""
        manager = AISearchManager(demo_mode=True)
        
        results = await manager.search_all_platforms(
            "test query",
            "example.com",
            platforms=["chatgpt", "perplexity"]
        )
        
        assert "chatgpt" in results
        assert "perplexity" in results
        assert len(results["chatgpt"]) > 0
        assert len(results["perplexity"]) > 0
    
    @pytest.mark.asyncio
    async def test_search_with_timeout(self):
        """Test recherche avec timeout"""
        manager = AISearchManager(demo_mode=True)
        
        # Mock un client qui timeout
        async def slow_search(query, domain):
            await asyncio.sleep(60)
            return []
        
        manager.clients["chatgpt"].search = slow_search
        
        results = await manager._search_with_timeout(
            "chatgpt", "test", "example.com", timeout=0.1
        )
        
        assert results == []  # Timeout donc résultat vide
    
    def test_calculate_global_score(self):
        """Test calcul score global"""
        manager = AISearchManager(demo_mode=True)
        
        results = {
            "chatgpt": [SearchResult(
                platform="ChatGPT", query="test", position=1,
                url="https://example.com", snippet="test",
                score=10.0, timestamp=datetime.now(),
                metadata={}
            )],
            "perplexity": [SearchResult(
                platform="Perplexity", query="test", position=2,
                url="https://example.com", snippet="test",
                score=8.0, timestamp=datetime.now(),
                metadata={}
            )]
        }
        
        global_score = manager.calculate_global_score(results)
        
        # Score = (10 * 0.4 + 8 * 0.3) / (0.4 + 0.3) = 9.14...
        assert 9 < global_score < 9.5
    
    def test_demo_mode_status(self):
        """Test statut mode démo"""
        manager = AISearchManager(demo_mode=True)
        status = manager.get_demo_mode_status()
        
        assert all(status.values())  # Tous en mode démo
        
        # Test avec clés API
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            manager = AISearchManager(demo_mode=False)
            status = manager.get_demo_mode_status()
            # ChatGPT ne devrait pas être en mode démo si clé fournie
            # (mais sera quand même en démo si module pas installé)


@pytest.mark.asyncio
async def test_concurrent_searches():
    """Test recherches concurrentes"""
    manager = AISearchManager(demo_mode=True)
    
    # Lancer plusieurs recherches en parallèle
    tasks = []
    for i in range(5):
        task = manager.search_all_platforms(
            f"query {i}",
            f"example{i}.com"
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Vérifier que toutes ont réussi
    assert len(results) == 5
    for result in results:
        assert len(result) == 4  # 4 plateformes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])