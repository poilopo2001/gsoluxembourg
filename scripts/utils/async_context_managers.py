#!/usr/bin/env python3
"""
Gestionnaires de contexte async pour GSO Toolkit
Développé par Sebastien Poletto - Expert GSO Luxembourg

Fournit des context managers pour une gestion propre des ressources async.
"""

import asyncio
import aiohttp
import httpx
from typing import Optional, Any, AsyncIterator
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

# Ajouter le chemin parent pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.rate_limiter import RateLimiter, RateLimitConfig
from utils.constants import API_TIMEOUTS, RATE_LIMITS, Platform

logger = logging.getLogger(__name__)


@asynccontextmanager
async def aiohttp_session(
    timeout: Optional[int] = None,
    headers: Optional[dict] = None
) -> AsyncIterator[aiohttp.ClientSession]:
    """
    Context manager pour session aiohttp avec gestion propre
    
    Args:
        timeout: Timeout en secondes (défaut: 30)
        headers: Headers HTTP à utiliser
        
    Yields:
        Session aiohttp configurée
    """
    timeout_config = aiohttp.ClientTimeout(
        total=timeout or API_TIMEOUTS["default"]
    )
    
    connector = aiohttp.TCPConnector(
        limit=100,  # Limite totale de connexions
        limit_per_host=30,  # Limite par host
        ttl_dns_cache=300  # Cache DNS 5 minutes
    )
    
    session = aiohttp.ClientSession(
        timeout=timeout_config,
        headers=headers or {},
        connector=connector
    )
    
    try:
        yield session
    finally:
        await session.close()
        # Attendre que toutes les connexions soient fermées
        await asyncio.sleep(0.1)


@asynccontextmanager
async def httpx_client(
    timeout: Optional[int] = None,
    headers: Optional[dict] = None
) -> AsyncIterator[httpx.AsyncClient]:
    """
    Context manager pour client httpx async
    
    Args:
        timeout: Timeout en secondes
        headers: Headers HTTP à utiliser
        
    Yields:
        Client httpx configuré
    """
    timeout_config = httpx.Timeout(
        timeout or API_TIMEOUTS["default"]
    )
    
    async with httpx.AsyncClient(
        timeout=timeout_config,
        headers=headers or {},
        follow_redirects=True,
        limits=httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100
        )
    ) as client:
        yield client


@asynccontextmanager
async def rate_limited_session(
    platform: Platform,
    timeout: Optional[int] = None
) -> AsyncIterator[aiohttp.ClientSession]:
    """
    Session aiohttp avec rate limiting intégré
    
    Args:
        platform: Plateforme pour laquelle appliquer le rate limit
        timeout: Timeout en secondes
        
    Yields:
        Session aiohttp avec rate limiting
    """
    rate_limiter = RateLimiter(
        RateLimitConfig(
            requests_per_minute=RATE_LIMITS.get(platform, 60)
        )
    )
    
    async with aiohttp_session(timeout=timeout) as session:
        # Créer un wrapper qui applique le rate limiting
        original_request = session.request
        
        async def rate_limited_request(*args, **kwargs):
            await rate_limiter.acquire()
            return await original_request(*args, **kwargs)
        
        # Remplacer la méthode request
        session.request = rate_limited_request
        
        yield session


@asynccontextmanager
async def api_client_context(
    api_key: str,
    platform: Platform,
    demo_mode: bool = False
) -> AsyncIterator[dict]:
    """
    Context manager complet pour client API
    
    Args:
        api_key: Clé API
        platform: Plateforme cible
        demo_mode: Mode démo activé
        
    Yields:
        Dictionnaire avec session et configuration
    """
    if demo_mode:
        # En mode démo, pas de vraie session
        yield {
            "session": None,
            "api_key": "demo_key",
            "platform": platform,
            "demo_mode": True
        }
        return
    
    headers = {}
    
    # Configuration headers selon plateforme
    if platform == Platform.CHATGPT:
        headers["Authorization"] = f"Bearer {api_key}"
    elif platform == Platform.PERPLEXITY:
        headers["Authorization"] = f"Bearer {api_key}"
    elif platform == Platform.CLAUDE:
        headers["x-api-key"] = api_key
    elif platform == Platform.GOOGLE_AI:
        # Google utilise paramètre URL au lieu de header
        pass
    
    async with rate_limited_session(
        platform=platform,
        timeout=API_TIMEOUTS["search"]
    ) as session:
        yield {
            "session": session,
            "api_key": api_key,
            "platform": platform,
            "demo_mode": False,
            "headers": headers
        }


class AsyncResourceManager:
    """
    Gestionnaire de ressources async avec nettoyage automatique
    """
    
    def __init__(self):
        self._resources: list[Any] = []
        self._cleanup_tasks: list[asyncio.Task] = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoie toutes les ressources"""
        # Annuler toutes les tâches en cours
        for task in self._cleanup_tasks:
            if not task.done():
                task.cancel()
        
        # Attendre que toutes les tâches soient terminées
        if self._cleanup_tasks:
            await asyncio.gather(
                *self._cleanup_tasks,
                return_exceptions=True
            )
        
        # Nettoyer les ressources
        for resource in self._resources:
            if hasattr(resource, "close"):
                try:
                    if asyncio.iscoroutinefunction(resource.close):
                        await resource.close()
                    else:
                        resource.close()
                except Exception as e:
                    logger.error(f"Erreur nettoyage ressource: {e}")
    
    def add_resource(self, resource: Any):
        """Ajoute une ressource à gérer"""
        self._resources.append(resource)
    
    def add_cleanup_task(self, task: asyncio.Task):
        """Ajoute une tâche de nettoyage"""
        self._cleanup_tasks.append(task)


@asynccontextmanager
async def parallel_api_calls(
    platforms: list[Platform],
    api_keys: dict[Platform, str],
    demo_mode: bool = False
) -> AsyncIterator[dict[Platform, dict]]:
    """
    Context manager pour appels API parallèles
    
    Args:
        platforms: Liste des plateformes
        api_keys: Clés API par plateforme
        demo_mode: Mode démo
        
    Yields:
        Dictionnaire des contextes par plateforme
    """
    contexts = {}
    
    async with AsyncResourceManager() as manager:
        # Créer les contextes pour chaque plateforme
        for platform in platforms:
            api_key = api_keys.get(platform, "")
            
            context = await api_client_context(
                api_key=api_key,
                platform=platform,
                demo_mode=demo_mode or not api_key
            ).__aenter__()
            
            contexts[platform] = context
            manager.add_resource(context)
        
        yield contexts


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation des context managers"""
    
    # Session simple
    async with aiohttp_session() as session:
        response = await session.get("https://example.com")
        data = await response.text()
    
    # Session avec rate limiting
    async with rate_limited_session(Platform.CHATGPT) as session:
        response = await session.post(
            "https://api.openai.com/v1/chat/completions",
            json={"model": "gpt-4", "messages": []}
        )
    
    # Appels parallèles multi-plateformes
    api_keys = {
        Platform.CHATGPT: "key1",
        Platform.PERPLEXITY: "key2"
    }
    
    async with parallel_api_calls(
        platforms=[Platform.CHATGPT, Platform.PERPLEXITY],
        api_keys=api_keys
    ) as contexts:
        # Utiliser les contextes
        for platform, ctx in contexts.items():
            if ctx["session"]:
                # Faire des appels API
                pass