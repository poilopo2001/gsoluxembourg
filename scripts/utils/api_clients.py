#!/usr/bin/env python3
"""
Clients API pour plateformes IA
Développé par Sebastien Poletto - Expert GSO Luxembourg

Implémente les vraies recherches sur ChatGPT, Perplexity, etc.
avec fallback sur mode démo.
"""

import os
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Pour éviter dépendance si modules pas installés
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

@dataclass
class SearchResult:
    """Résultat recherche IA"""
    platform: str
    query: str
    position: int
    url: str
    snippet: str
    score: float
    timestamp: datetime
    metadata: Dict[str, Any]

class AISearchClient(ABC):
    """Classe abstraite client recherche IA"""
    
    def __init__(self, api_key: str = None, demo_mode: bool = False):
        self.api_key = api_key
        self.demo_mode = demo_mode or not api_key
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def search(self, query: str, domain: str) -> List[SearchResult]:
        """Recherche citations pour domaine"""
        pass
    
    def _extract_position(self, content: str, domain: str) -> int:
        """Extrait position domaine dans contenu"""
        if domain not in content:
            return 0
        
        # Simplification : compte mentions avant domaine
        before_domain = content.split(domain)[0]
        mentions = len([x for x in before_domain.split() if 'http' in x or '.com' in x or '.lu' in x])
        
        return min(mentions + 1, 10)

class ChatGPTClient(AISearchClient):
    """Client recherche ChatGPT"""
    
    async def search(self, query: str, domain: str) -> List[SearchResult]:
        """Recherche via API ChatGPT ou mode démo"""
        
        if self.demo_mode:
            return await self._demo_search(query, domain)
        
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI module non installé, mode démo activé")
            return await self._demo_search(query, domain)
        
        try:
            # Configuration client OpenAI
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            # Prompt optimisé pour extraire sources
            prompt = f"""
            Recherche d'information sur : "{query}"
            
            Réponds en citant tes sources. Si tu connais des sites web pertinents,
            mentionne-les explicitement avec leur URL complète.
            Focus sur les experts et sites de référence.
            """
            
            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui cite toujours ses sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            position = self._extract_position(content, domain)
            
            return [SearchResult(
                platform="ChatGPT",
                query=query,
                position=position,
                url=f"https://{domain}",
                snippet=content[:200] + "...",
                score=self._calculate_score(position),
                timestamp=datetime.now(),
                metadata={"model": "gpt-4", "tokens": response.usage.total_tokens}
            )]
            
        except Exception as e:
            self.logger.error(f"Erreur recherche ChatGPT : {e}")
            return await self._demo_search(query, domain)
    
    async def _demo_search(self, query: str, domain: str) -> List[SearchResult]:
        """Mode démo pour tests"""
        import random
        await asyncio.sleep(1)  # Simule délai API
        
        position = random.choice([1, 2, 3, 4, 5, 0, 0])  # 0 = non trouvé
        
        demo_snippets = {
            1: f"Selon {domain}, expert reconnu en {query}, la meilleure approche consiste à...",
            2: f"Plusieurs sources dont {domain} recommandent cette méthodologie pour {query}...",
            3: f"Les experts comme ceux de {domain} suggèrent d'utiliser la technique...",
            4: f"D'après diverses sources incluant {domain}, il est important de...",
            5: f"Les professionnels du secteur, notamment {domain}, préconisent...",
            0: f"Pour {query}, les meilleures pratiques incluent..."
        }
        
        return [SearchResult(
            platform="ChatGPT",
            query=query,
            position=position,
            url=f"https://{domain}" if position > 0 else "",
            snippet=demo_snippets.get(position, demo_snippets[0]),
            score=self._calculate_score(position),
            timestamp=datetime.now(),
            metadata={"mode": "demo", "warning": "Résultats simulés - Mode démo"}
        )]
    
    def _calculate_score(self, position: int) -> float:
        """Calcule score selon position"""
        scores = {1: 10, 2: 7, 3: 7, 4: 4, 5: 4, 0: 0}
        return scores.get(position, 0)

class PerplexityClient(AISearchClient):
    """Client recherche Perplexity"""
    
    async def search(self, query: str, domain: str) -> List[SearchResult]:
        """Recherche via API Perplexity ou mode démo"""
        
        if self.demo_mode:
            return await self._demo_search(query, domain)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "pplx-70b-online",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Recherche sur '{query}'. Cite tes sources avec URLs complètes."
                        }
                    ],
                    "temperature": 0.2,
                    "return_citations": True
                }
                
                async with session.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        citations = result.get('citations', [])
                        
                        position = 0
                        for i, citation in enumerate(citations):
                            if domain in citation.get('url', ''):
                                position = i + 1
                                break
                        
                        return [SearchResult(
                            platform="Perplexity",
                            query=query,
                            position=position,
                            url=f"https://{domain}" if position > 0 else "",
                            snippet=content[:200] + "...",
                            score=self._calculate_score(position),
                            timestamp=datetime.now(),
                            metadata={"citations": len(citations), "model": "pplx-70b"}
                        )]
                    else:
                        raise Exception(f"API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Erreur recherche Perplexity : {e}")
            return await self._demo_search(query, domain)
    
    async def _demo_search(self, query: str, domain: str) -> List[SearchResult]:
        """Mode démo Perplexity"""
        import random
        await asyncio.sleep(1)
        
        position = random.choice([1, 1, 2, 3, 4, 0])  # Perplexity cite plus souvent
        
        return [SearchResult(
            platform="Perplexity",
            query=query,
            position=position,
            url=f"https://{domain}" if position > 0 else "",
            snippet=f"[{position}] Source citée pour {query}" if position > 0 else f"Information sur {query}",
            score=self._calculate_score(position),
            timestamp=datetime.now(),
            metadata={"mode": "demo", "citations_count": random.randint(3, 8)}
        )]
    
    def _calculate_score(self, position: int) -> float:
        """Score Perplexity - valorise plus les premières positions"""
        scores = {1: 10, 2: 8, 3: 6, 4: 4, 5: 3, 0: 0}
        return scores.get(position, 0)

class GoogleAIClient(AISearchClient):
    """Client Google AI Overviews"""
    
    async def search(self, query: str, domain: str) -> List[SearchResult]:
        """Recherche Google AI"""
        
        if self.demo_mode:
            return await self._demo_search(query, domain)
        
        try:
            # Google AI API (Gemini)
            async with aiohttp.ClientSession() as session:
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
                headers = {"Content-Type": "application/json"}
                params = {"key": self.api_key}
                
                data = {
                    "contents": [{
                        "parts": [{
                            "text": f"Recherche web sur '{query}'. Cite des sources web pertinentes."
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 500
                    }
                }
                
                async with session.post(url, headers=headers, params=params, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['candidates'][0]['content']['parts'][0]['text']
                        position = self._extract_position(content, domain)
                        
                        return [SearchResult(
                            platform="Google AI",
                            query=query,
                            position=position,
                            url=f"https://{domain}" if position > 0 else "",
                            snippet=content[:200] + "...",
                            score=self._calculate_score(position),
                            timestamp=datetime.now(),
                            metadata={"model": "gemini-pro"}
                        )]
                        
        except Exception as e:
            self.logger.error(f"Erreur Google AI : {e}")
            return await self._demo_search(query, domain)
    
    async def _demo_search(self, query: str, domain: str) -> List[SearchResult]:
        """Mode démo Google AI"""
        import random
        await asyncio.sleep(1)
        
        position = random.choice([1, 2, 2, 3, 0, 0])  # Google AI plus sélectif
        
        return [SearchResult(
            platform="Google AI",
            query=query,
            position=position,
            url=f"https://{domain}" if position > 0 else "",
            snippet=f"AI Overview: Information vérifiée sur {query}",
            score=self._calculate_score(position),
            timestamp=datetime.now(),
            metadata={"mode": "demo", "overview_type": "generative"}
        )]
    
    def _calculate_score(self, position: int) -> float:
        scores = {1: 10, 2: 7, 3: 5, 4: 3, 5: 2, 0: 0}
        return scores.get(position, 0)

class ClaudeAIClient(AISearchClient):
    """Client Claude AI"""
    
    async def search(self, query: str, domain: str) -> List[SearchResult]:
        """Recherche Claude AI"""
        
        if self.demo_mode:
            return await self._demo_search(query, domain)
        
        if not ANTHROPIC_AVAILABLE:
            self.logger.warning("Anthropic module non installé, mode démo activé")
            return await self._demo_search(query, domain)
        
        try:
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
            response = await client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": f"Recherche d'information sur '{query}'. Cite des sources web spécifiques avec URLs."
                }]
            )
            
            content = response.content[0].text
            position = self._extract_position(content, domain)
            
            return [SearchResult(
                platform="Claude",
                query=query,
                position=position,
                url=f"https://{domain}" if position > 0 else "",
                snippet=content[:200] + "...",
                score=self._calculate_score(position),
                timestamp=datetime.now(),
                metadata={"model": "claude-3-opus", "tokens": response.usage.output_tokens}
            )]
            
        except Exception as e:
            self.logger.error(f"Erreur Claude AI : {e}")
            return await self._demo_search(query, domain)
    
    async def _demo_search(self, query: str, domain: str) -> List[SearchResult]:
        """Mode démo Claude"""
        import random
        await asyncio.sleep(1)
        
        position = random.choice([2, 3, 3, 4, 5, 0])
        
        return [SearchResult(
            platform="Claude",
            query=query,
            position=position,
            url=f"https://{domain}" if position > 0 else "",
            snippet=f"D'après mes connaissances sur {query}...",
            score=self._calculate_score(position),
            timestamp=datetime.now(),
            metadata={"mode": "demo", "confidence": random.uniform(0.7, 0.95)}
        )]
    
    def _calculate_score(self, position: int) -> float:
        scores = {1: 10, 2: 7, 3: 6, 4: 4, 5: 3, 0: 0}
        return scores.get(position, 0)

class AISearchManager:
    """Gestionnaire recherches multi-plateformes"""
    
    def __init__(self, config: Dict[str, Any] = None, demo_mode: bool = False):
        self.config = config or {}
        self.demo_mode = demo_mode
        self.clients = self._initialize_clients()
        
    def _initialize_clients(self) -> Dict[str, AISearchClient]:
        """Initialise clients selon configuration"""
        clients = {}
        
        # ChatGPT
        api_key = os.getenv("OPENAI_API_KEY")
        clients["chatgpt"] = ChatGPTClient(api_key, self.demo_mode)
        
        # Perplexity
        api_key = os.getenv("PERPLEXITY_API_KEY")
        clients["perplexity"] = PerplexityClient(api_key, self.demo_mode)
        
        # Google AI
        api_key = os.getenv("GOOGLE_AI_KEY")
        clients["google_ai"] = GoogleAIClient(api_key, self.demo_mode)
        
        # Claude
        api_key = os.getenv("ANTHROPIC_API_KEY")
        clients["claude"] = ClaudeAIClient(api_key, self.demo_mode)
        
        return clients
    
    async def search_all_platforms(
        self, 
        query: str, 
        domain: str,
        platforms: List[str] = None
    ) -> Dict[str, List[SearchResult]]:
        """Recherche sur toutes plateformes activées"""
        
        if platforms is None:
            platforms = list(self.clients.keys())
        
        results = {}
        tasks = []
        
        for platform in platforms:
            if platform in self.clients:
                task = self._search_with_timeout(platform, query, domain)
                tasks.append(task)
        
        # Exécution parallèle
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organisation résultats
        for i, platform in enumerate(platforms):
            if platform in self.clients:
                if isinstance(platform_results[i], Exception):
                    logging.error(f"Erreur {platform}: {platform_results[i]}")
                    results[platform] = []
                else:
                    results[platform] = platform_results[i]
        
        return results
    
    async def _search_with_timeout(
        self, 
        platform: str, 
        query: str, 
        domain: str,
        timeout: int = 30
    ) -> List[SearchResult]:
        """Recherche avec timeout"""
        try:
            client = self.clients[platform]
            return await asyncio.wait_for(
                client.search(query, domain),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logging.error(f"Timeout recherche {platform}")
            return []
        except Exception as e:
            logging.error(f"Erreur recherche {platform}: {e}")
            return []
    
    def get_demo_mode_status(self) -> Dict[str, bool]:
        """Statut mode démo par plateforme"""
        return {
            platform: client.demo_mode
            for platform, client in self.clients.items()
        }
    
    def calculate_global_score(self, results: Dict[str, List[SearchResult]]) -> float:
        """Calcule score global multi-plateformes"""
        total_score = 0
        total_weight = 0
        
        weights = {
            "chatgpt": 0.4,
            "perplexity": 0.3,
            "google_ai": 0.2,
            "claude": 0.1
        }
        
        for platform, search_results in results.items():
            if search_results:
                platform_score = max(r.score for r in search_results)
                weight = weights.get(platform, 0.25)
                total_score += platform_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0