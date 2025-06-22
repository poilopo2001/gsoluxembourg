#!/usr/bin/env python3
"""
Module de gestion du rate limiting et des erreurs
Développé par Sebastien Poletto - Expert GSO Luxembourg

Implémente un système robuste de rate limiting et gestion des erreurs.
"""

import asyncio
import time
from typing import Dict, Optional, Any, Callable, TypeVar, Union
from functools import wraps
from dataclasses import dataclass, field
from collections import deque
import logging
from datetime import datetime, timedelta
import aiohttp
import httpx
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RateLimitStrategy(Enum):
    """Stratégies de rate limiting"""
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """Configuration pour le rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: Optional[int] = None
    burst_size: Optional[int] = None
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    retry_after_rate_limit: bool = True
    max_retries: int = 3
    backoff_factor: float = 2.0


class RateLimiter:
    """
    Gestionnaire de rate limiting avec support pour plusieurs stratégies
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.request_times: deque = deque()
        self.tokens = config.burst_size or config.requests_per_minute
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquiert le droit de faire une requête"""
        async with self._lock:
            if self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                await self._sliding_window_acquire()
            elif self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                await self._token_bucket_acquire()
            else:
                await self._fixed_window_acquire()
    
    async def _sliding_window_acquire(self) -> None:
        """Implémentation sliding window"""
        now = time.time()
        minute_ago = now - 60
        
        # Nettoyer les anciennes requêtes
        while self.request_times and self.request_times[0] < minute_ago:
            self.request_times.popleft()
        
        # Vérifier la limite par minute
        if len(self.request_times) >= self.config.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit atteint, attente de {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
                return await self._sliding_window_acquire()
        
        # Vérifier la limite par heure si définie
        if self.config.requests_per_hour:
            hour_ago = now - 3600
            hour_requests = sum(1 for t in self.request_times if t > hour_ago)
            if hour_requests >= self.config.requests_per_hour:
                sleep_time = 3600 - (now - next(t for t in self.request_times if t > hour_ago))
                if sleep_time > 0:
                    logger.info(f"Limite horaire atteinte, attente de {sleep_time:.1f}s")
                    await asyncio.sleep(sleep_time)
                    return await self._sliding_window_acquire()
        
        self.request_times.append(now)
    
    async def _token_bucket_acquire(self) -> None:
        """Implémentation token bucket"""
        now = time.time()
        
        # Remplir le bucket
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * (self.config.requests_per_minute / 60)
        self.tokens = min(self.config.burst_size or self.config.requests_per_minute, 
                         self.tokens + tokens_to_add)
        self.last_refill = now
        
        if self.tokens < 1:
            sleep_time = (1 - self.tokens) * 60 / self.config.requests_per_minute
            logger.info(f"Pas de tokens disponibles, attente de {sleep_time:.1f}s")
            await asyncio.sleep(sleep_time)
            return await self._token_bucket_acquire()
        
        self.tokens -= 1
    
    async def _fixed_window_acquire(self) -> None:
        """Implémentation fixed window (plus simple mais moins précise)"""
        # Pour simplicité, on utilise sliding window avec fenêtre de 60s
        await self._sliding_window_acquire()


class RetryHandler:
    """
    Gestionnaire de retry avec backoff exponentiel
    """
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0,
                 max_backoff: float = 300.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
    
    async def execute_with_retry(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Exécute une fonction avec retry automatique
        
        Args:
            func: Fonction à exécuter
            *args, **kwargs: Arguments pour la fonction
            
        Returns:
            Résultat de la fonction
            
        Raises:
            Exception: Si toutes les tentatives échouent
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            
            except (aiohttp.ClientTimeout, httpx.TimeoutException) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    sleep_time = min(self.backoff_factor ** attempt, self.max_backoff)
                    logger.warning(f"Timeout, tentative {attempt + 1}/{self.max_retries}, "
                                 f"attente {sleep_time}s: {e}")
                    await asyncio.sleep(sleep_time)
                else:
                    logger.error(f"Timeout après {self.max_retries} tentatives")
            
            except (aiohttp.ClientResponseError, httpx.HTTPStatusError) as e:
                # Gérer spécifiquement les erreurs de rate limit
                if hasattr(e, 'status') and e.status == 429:
                    retry_after = self._extract_retry_after(e)
                    if retry_after and attempt < self.max_retries - 1:
                        logger.warning(f"Rate limit (429), attente {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                
                last_exception = e
                if attempt < self.max_retries - 1:
                    sleep_time = min(self.backoff_factor ** attempt, self.max_backoff)
                    logger.warning(f"Erreur HTTP {getattr(e, 'status', 'unknown')}, "
                                 f"tentative {attempt + 1}/{self.max_retries}, "
                                 f"attente {sleep_time}s")
                    await asyncio.sleep(sleep_time)
                else:
                    logger.error(f"Erreur HTTP après {self.max_retries} tentatives")
            
            except Exception as e:
                # Autres exceptions non gérées
                logger.error(f"Erreur inattendue: {type(e).__name__}: {e}")
                raise
        
        raise last_exception or Exception("Échec après toutes les tentatives")
    
    def _extract_retry_after(self, error: Union[aiohttp.ClientResponseError, 
                                               httpx.HTTPStatusError]) -> Optional[float]:
        """Extrait le délai Retry-After de l'erreur"""
        try:
            if isinstance(error, aiohttp.ClientResponseError):
                headers = error.headers
            else:  # httpx
                headers = error.response.headers
            
            retry_after = headers.get('Retry-After')
            if retry_after:
                # Peut être en secondes ou une date HTTP
                try:
                    return float(retry_after)
                except ValueError:
                    # Essayer de parser comme date HTTP
                    from email.utils import parsedate_to_datetime
                    retry_date = parsedate_to_datetime(retry_after)
                    return max(0, (retry_date - datetime.now()).total_seconds())
        except Exception:
            pass
        
        return None


def rate_limited(rate_limiter: RateLimiter):
    """
    Décorateur pour appliquer le rate limiting à une fonction async
    
    Args:
        rate_limiter: Instance de RateLimiter à utiliser
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            await rate_limiter.acquire()
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def with_retry(retry_handler: Optional[RetryHandler] = None):
    """
    Décorateur pour ajouter retry automatique à une fonction async
    
    Args:
        retry_handler: Instance de RetryHandler (ou utilise défaut)
    """
    handler = retry_handler or RetryHandler()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await handler.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator


class APIErrorHandler:
    """
    Gestionnaire centralisé des erreurs API
    """
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.last_errors: Dict[str, datetime] = {}
    
    def handle_error(self, platform: str, error: Exception) -> bool:
        """
        Gère une erreur et décide si on doit continuer
        
        Args:
            platform: Nom de la plateforme
            error: Exception survenue
            
        Returns:
            True si on peut continuer, False sinon
        """
        error_key = f"{platform}:{type(error).__name__}"
        now = datetime.now()
        
        # Réinitialiser le compteur si dernière erreur > 1 heure
        if error_key in self.last_errors:
            if now - self.last_errors[error_key] > timedelta(hours=1):
                self.error_counts[error_key] = 0
        
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_errors[error_key] = now
        
        # Si trop d'erreurs consécutives, arrêter
        if self.error_counts[error_key] > 10:
            logger.error(f"Trop d'erreurs pour {platform}, arrêt temporaire")
            return False
        
        return True
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des erreurs"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "errors_by_type": dict(self.error_counts),
            "last_error_times": {k: v.isoformat() for k, v in self.last_errors.items()}
        }


# Instances globales pour faciliter l'utilisation
default_rate_limiter = RateLimiter(RateLimitConfig())
default_retry_handler = RetryHandler()
error_handler = APIErrorHandler()