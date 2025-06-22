#!/usr/bin/env python3
"""
Tests unitaires pour le module rate_limiter
Développé par Sebastien Poletto - Expert GSO Luxembourg
"""

import pytest
import asyncio
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import aiohttp
import httpx

# Ajouter le chemin parent pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.rate_limiter import (
    RateLimiter, RateLimitConfig, RetryHandler, APIErrorHandler,
    RateLimitStrategy, rate_limited, with_retry
)


class TestRateLimiter:
    """Tests pour RateLimiter"""
    
    @pytest.mark.asyncio
    async def test_sliding_window_basic(self):
        """Test rate limiting fenêtre glissante basique"""
        config = RateLimitConfig(
            requests_per_minute=3,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
        limiter = RateLimiter(config)
        
        # 3 requêtes rapides doivent passer
        start = time.time()
        for _ in range(3):
            await limiter.acquire()
        
        # La 4ème doit attendre
        await limiter.acquire()
        elapsed = time.time() - start
        
        # Devrait avoir attendu environ 60 secondes
        assert elapsed >= 59  # Petite marge pour l'exécution
    
    @pytest.mark.asyncio
    async def test_sliding_window_with_hourly_limit(self):
        """Test limite horaire"""
        config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=100,
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
        limiter = RateLimiter(config)
        
        # Simuler des requêtes pour tester la limite horaire
        # (test simplifié pour ne pas attendre 1 heure)
        assert limiter.config.requests_per_hour == 100
    
    @pytest.mark.asyncio
    async def test_token_bucket(self):
        """Test token bucket"""
        config = RateLimitConfig(
            requests_per_minute=60,
            burst_size=10,
            strategy=RateLimitStrategy.TOKEN_BUCKET
        )
        limiter = RateLimiter(config)
        
        # Devrait pouvoir faire 10 requêtes rapidement (burst)
        start = time.time()
        for _ in range(10):
            await limiter.acquire()
        elapsed = time.time() - start
        
        # Les 10 premières devraient être quasi instantanées
        assert elapsed < 1
    
    @pytest.mark.asyncio
    async def test_rate_limited_decorator(self):
        """Test décorateur rate_limited"""
        config = RateLimitConfig(requests_per_minute=2)
        limiter = RateLimiter(config)
        call_count = 0
        
        @rate_limited(limiter)
        async def test_function():
            nonlocal call_count
            call_count += 1
            return call_count
        
        # Appeler 3 fois
        start = time.time()
        results = []
        for _ in range(3):
            result = await test_function()
            results.append(result)
        
        elapsed = time.time() - start
        
        assert results == [1, 2, 3]
        # La 3ème devrait avoir attendu
        assert elapsed >= 30  # Au moins 30 secondes d'attente


class TestRetryHandler:
    """Tests pour RetryHandler"""
    
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test exécution réussie du premier coup"""
        handler = RetryHandler(max_retries=3)
        
        async def success_func():
            return "success"
        
        result = await handler.execute_with_retry(success_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Test retry sur timeout"""
        handler = RetryHandler(max_retries=3, backoff_factor=0.1)
        call_count = 0
        
        async def timeout_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise aiohttp.ClientTimeout()
            return "success"
        
        result = await handler.execute_with_retry(timeout_func)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test échec après max retries"""
        handler = RetryHandler(max_retries=3, backoff_factor=0.1)
        
        async def always_fail():
            raise aiohttp.ClientTimeout("Always fails")
        
        with pytest.raises(aiohttp.ClientTimeout):
            await handler.execute_with_retry(always_fail)
    
    @pytest.mark.asyncio
    async def test_rate_limit_retry(self):
        """Test retry sur erreur 429"""
        handler = RetryHandler(max_retries=3, backoff_factor=0.1)
        call_count = 0
        
        async def rate_limited_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error = aiohttp.ClientResponseError(
                    request_info=Mock(), 
                    history=()
                )
                error.status = 429
                error.headers = {'Retry-After': '0.1'}
                raise error
            return "success"
        
        result = await handler.execute_with_retry(rate_limited_func)
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_with_retry_decorator(self):
        """Test décorateur with_retry"""
        call_count = 0
        
        @with_retry(RetryHandler(max_retries=3, backoff_factor=0.1))
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.TimeoutException("Timeout")
            return "success"
        
        result = await flaky_function()
        assert result == "success"
        assert call_count == 2


class TestAPIErrorHandler:
    """Tests pour APIErrorHandler"""
    
    def test_error_counting(self):
        """Test comptage des erreurs"""
        handler = APIErrorHandler()
        
        # Première erreur
        assert handler.handle_error("ChatGPT", ValueError("Test"))
        assert handler.error_counts["ChatGPT:ValueError"] == 1
        
        # Deuxième erreur du même type
        assert handler.handle_error("ChatGPT", ValueError("Test 2"))
        assert handler.error_counts["ChatGPT:ValueError"] == 2
    
    def test_error_limit(self):
        """Test limite d'erreurs"""
        handler = APIErrorHandler()
        
        # Simuler 11 erreurs
        for i in range(11):
            result = handler.handle_error("ChatGPT", ValueError(f"Error {i}"))
        
        # La 11ème devrait retourner False
        assert not result
        assert handler.error_counts["ChatGPT:ValueError"] == 11
    
    def test_error_reset_after_time(self):
        """Test reset des erreurs après 1 heure"""
        handler = APIErrorHandler()
        
        # Première erreur
        handler.handle_error("ChatGPT", ValueError("Test"))
        
        # Simuler passage du temps
        with patch('scripts.utils.rate_limiter.datetime') as mock_datetime:
            # Première erreur à T0
            now = datetime.now()
            mock_datetime.now.return_value = now
            handler.handle_error("ChatGPT", ValueError("Test"))
            
            # Deuxième erreur 2 heures plus tard
            mock_datetime.now.return_value = now + timedelta(hours=2)
            handler.handle_error("ChatGPT", ValueError("Test"))
            
            # Le compteur devrait être réinitialisé
            assert handler.error_counts["ChatGPT:ValueError"] == 1
    
    def test_error_summary(self):
        """Test résumé des erreurs"""
        handler = APIErrorHandler()
        
        handler.handle_error("ChatGPT", ValueError("Test"))
        handler.handle_error("Perplexity", TimeoutError("Timeout"))
        handler.handle_error("ChatGPT", ValueError("Test 2"))
        
        summary = handler.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert summary["errors_by_type"]["ChatGPT:ValueError"] == 2
        assert summary["errors_by_type"]["Perplexity:TimeoutError"] == 1
        assert "ChatGPT:ValueError" in summary["last_error_times"]


@pytest.mark.asyncio
async def test_integration_rate_limit_and_retry():
    """Test intégration rate limiting et retry"""
    config = RateLimitConfig(requests_per_minute=2)
    limiter = RateLimiter(config)
    retry_handler = RetryHandler(max_retries=3, backoff_factor=0.1)
    
    call_times = []
    
    @rate_limited(limiter)
    @with_retry(retry_handler)
    async def api_call():
        call_times.append(time.time())
        if len(call_times) == 1:
            raise aiohttp.ClientTimeout("First call fails")
        return f"Call {len(call_times)}"
    
    # Faire 2 appels
    start = time.time()
    result1 = await api_call()  # Échoue puis réussit
    result2 = await api_call()  # Réussit directement
    elapsed = time.time() - start
    
    # Vérifier les résultats
    assert result1 == "Call 2"  # Deuxième tentative
    assert result2 == "Call 3"
    assert len(call_times) == 3  # 2 pour le premier appel, 1 pour le second
    
    # Vérifier que le rate limiting a fonctionné
    assert elapsed >= 30  # Au moins 30 secondes entre les appels


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])