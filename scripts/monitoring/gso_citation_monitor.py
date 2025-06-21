#!/usr/bin/env python3
"""
GSO Citation Monitor - Surveillance automatisée des citations IA
Développé par Sebastien Poletto - Expert GSO Luxembourg

Ce script implémente la méthodologie ATOMIC-GSO© pour monitorer
la visibilité dans ChatGPT, Perplexity, Google AI et Claude.

Utilisation:
    python gso_citation_monitor.py --domain exemple.com --queries queries.json
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import requests
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

@dataclass
class CitationResult:
    """Structure résultat de citation"""
    platform: str
    query: str
    position: int
    score: int
    content_snippet: str
    url: str
    timestamp: datetime
    
class GSACitationMonitor:
    """
    Moniteur citations GSO - Méthodologie ATOMIC-GSO©
    
    Surveillance automatisée de la visibilité dans :
    - ChatGPT Search
    - Perplexity AI  
    - Google AI Overviews
    - Claude AI (via API)
    """
    
    def __init__(self, domain: str, config_path: str = None):
        self.domain = domain
        self.config = self._load_config(config_path)
        self.results_history = []
        self.setup_logging()
        
    def setup_logging(self):
        """Configuration logging avancé"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - GSO Monitor - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'gso_monitor_{self.domain}_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict:
        """Charge configuration monitoring"""
        default_config = {
            "scoring": {
                "first_position": 10,
                "top_3": 7, 
                "others": 4,
                "not_found": 0
            },
            "platforms": {
                "chatgpt": {"enabled": True, "weight": 0.4},
                "perplexity": {"enabled": True, "weight": 0.3},
                "google_ai": {"enabled": True, "weight": 0.2},
                "claude": {"enabled": True, "weight": 0.1}
            },
            "alerts": {
                "drop_threshold": 20,  # % baisse pour alerte
                "email_notifications": True
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
    
    async def test_chatgpt_visibility(self, queries: List[str]) -> List[CitationResult]:
        """
        Test visibilité ChatGPT - Méthode FLIP©
        F.L.I.P = Format, Links, Intent, Position
        """
        results = []
        console.print("[bold blue]🤖 Test ChatGPT Search...[/bold blue]")
        
        for query in track(queries, description="Analyse ChatGPT"):
            try:
                # Simulation API ChatGPT (remplacer par vraie API)
                result = await self._simulate_chatgpt_search(query)
                results.append(result)
                
                # Délai entre requêtes (respect rate limits)
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur ChatGPT pour '{query}': {e}")
                
        return results
    
    async def test_perplexity_visibility(self, queries: List[str]) -> List[CitationResult]:
        """Test visibilité Perplexity AI"""
        results = []
        console.print("[bold green]🔍 Test Perplexity AI...[/bold green]")
        
        for query in track(queries, description="Analyse Perplexity"):
            try:
                result = await self._simulate_perplexity_search(query)
                results.append(result)
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur Perplexity pour '{query}': {e}")
                
        return results
    
    async def test_google_ai_visibility(self, queries: List[str]) -> List[CitationResult]:
        """Test visibilité Google AI Overviews"""
        results = []
        console.print("[bold yellow]🔍 Test Google AI Overviews...[/bold yellow]")
        
        for query in track(queries, description="Analyse Google AI"):
            try:
                result = await self._simulate_google_ai_search(query)
                results.append(result)
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur Google AI pour '{query}': {e}")
                
        return results
    
    async def test_claude_visibility(self, queries: List[str]) -> List[CitationResult]:
        """Test visibilité Claude AI"""
        results = []
        console.print("[bold purple]🤖 Test Claude AI...[/bold purple]")
        
        for query in track(queries, description="Analyse Claude"):
            try:
                result = await self._simulate_claude_search(query)
                results.append(result)
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur Claude pour '{query}': {e}")
                
        return results
    
    async def _simulate_chatgpt_search(self, query: str) -> CitationResult:
        """Simulation recherche ChatGPT (à remplacer par vraie API)"""
        # Ici, implémentation réelle API ChatGPT
        # Pour la démo, simulation de résultat
        
        import random
        positions = [1, 2, 3, 4, 5, 0]  # 0 = non trouvé
        position = random.choice(positions)
        
        score = self._calculate_position_score(position)
        
        return CitationResult(
            platform="ChatGPT",
            query=query,
            position=position,
            score=score,
            content_snippet=f"Snippet simulé pour {query}",
            url=f"https://{self.domain}/page-exemple",
            timestamp=datetime.now()
        )
    
    async def _simulate_perplexity_search(self, query: str) -> CitationResult:
        """Simulation recherche Perplexity"""
        import random
        position = random.choice([1, 2, 3, 4, 5, 0])
        score = self._calculate_position_score(position)
        
        return CitationResult(
            platform="Perplexity",
            query=query,
            position=position,
            score=score,
            content_snippet=f"Perplexity snippet pour {query}",
            url=f"https://{self.domain}/page-exemple",
            timestamp=datetime.now()
        )
    
    async def _simulate_google_ai_search(self, query: str) -> CitationResult:
        """Simulation recherche Google AI"""
        import random
        position = random.choice([1, 2, 3, 4, 5, 0])
        score = self._calculate_position_score(position)
        
        return CitationResult(
            platform="Google AI",
            query=query,
            position=position,
            score=score,
            content_snippet=f"Google AI snippet pour {query}",
            url=f"https://{self.domain}/page-exemple",
            timestamp=datetime.now()
        )
    
    async def _simulate_claude_search(self, query: str) -> CitationResult:
        """Simulation recherche Claude"""
        import random
        position = random.choice([1, 2, 3, 4, 5, 0])
        score = self._calculate_position_score(position)
        
        return CitationResult(
            platform="Claude",
            query=query,
            position=position,
            score=score,
            content_snippet=f"Claude snippet pour {query}",
            url=f"https://{self.domain}/page-exemple",
            timestamp=datetime.now()
        )
    
    def _calculate_position_score(self, position: int) -> int:
        """Calcul score selon position - Méthodologie ATOMIC-GSO©"""
        if position == 1:
            return self.config["scoring"]["first_position"]
        elif position <= 3:
            return self.config["scoring"]["top_3"]
        elif position > 3:
            return self.config["scoring"]["others"]
        else:
            return self.config["scoring"]["not_found"]
    
    async def run_full_monitoring(self, queries: List[str]) -> Dict:
        """Exécution monitoring complet - Framework ATOMIC-GSO©"""
        console.print(f"\n[bold cyan]🚀 Début monitoring GSO pour {self.domain}[/bold cyan]")
        console.print(f"📊 {len(queries)} requêtes à tester")
        console.print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        all_results = []
        
        # Test sur toutes les plateformes
        if self.config["platforms"]["chatgpt"]["enabled"]:
            chatgpt_results = await self.test_chatgpt_visibility(queries)
            all_results.extend(chatgpt_results)
            
        if self.config["platforms"]["perplexity"]["enabled"]:
            perplexity_results = await self.test_perplexity_visibility(queries)
            all_results.extend(perplexity_results)
            
        if self.config["platforms"]["google_ai"]["enabled"]:
            google_results = await self.test_google_ai_visibility(queries)
            all_results.extend(google_results)
            
        if self.config["platforms"]["claude"]["enabled"]:
            claude_results = await self.test_claude_visibility(queries)
            all_results.extend(claude_results)
        
        # Calcul scores et métriques
        analysis = self._analyze_results(all_results)
        
        # Génération rapport
        self._generate_report(analysis, all_results)
        
        # Sauvegarde historique
        self._save_results(all_results)
        
        return analysis
    
    def _analyze_results(self, results: List[CitationResult]) -> Dict:
        """Analyse complète résultats GSO"""
        if not results:
            return {"error": "Aucun résultat à analyser"}
        
        # DataFrame pour analysis
        df = pd.DataFrame([
            {
                'platform': r.platform,
                'query': r.query,
                'position': r.position,
                'score': r.score,
                'found': r.position > 0
            } for r in results
        ])
        
        # Métriques globales
        total_score = df['score'].sum()
        max_possible = len(results) * self.config["scoring"]["first_position"]
        visibility_percentage = (total_score / max_possible) * 100
        
        # Métriques par plateforme
        platform_stats = df.groupby('platform').agg({
            'score': 'sum',
            'found': 'mean',
            'position': lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0
        }).round(2)
        
        # Top queries
        query_stats = df.groupby('query').agg({
            'score': 'sum',
            'found': 'mean'
        }).sort_values('score', ascending=False)
        
        analysis = {
            "global_score": total_score,
            "max_possible_score": max_possible,
            "visibility_percentage": round(visibility_percentage, 2),
            "citations_found": df['found'].sum(),
            "total_tests": len(results),
            "citation_rate": round(df['found'].mean() * 100, 2),
            "average_position": round(df[df['position'] > 0]['position'].mean(), 2),
            "platform_performance": platform_stats.to_dict(),
            "top_queries": query_stats.head(10).to_dict(),
            "recommendations": self._generate_recommendations(df)
        }
        
        return analysis
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Génération recommandations automatiques"""
        recommendations = []
        
        # Analyse par plateforme
        platform_performance = df.groupby('platform')['found'].mean()
        
        for platform, success_rate in platform_performance.items():
            if success_rate < 0.3:
                recommendations.append(
                    f"🔴 {platform}: Taux de citation faible ({success_rate:.1%}). "
                    f"Optimiser contenu selon spécificités {platform}"
                )
            elif success_rate < 0.6:
                recommendations.append(
                    f"🟡 {platform}: Performance modérée ({success_rate:.1%}). "
                    f"Appliquer techniques avancées ATOMIC-GSO©"
                )
            else:
                recommendations.append(
                    f"🟢 {platform}: Excellente performance ({success_rate:.1%}). "
                    f"Maintenir stratégie actuelle"
                )
        
        # Recommandations générales
        avg_position = df[df['position'] > 0]['position'].mean()
        if avg_position > 3:
            recommendations.append(
                "📈 Position moyenne élevée. Implémenter technique FLIP© "
                "pour améliorer ranking ChatGPT"
            )
        
        if df['found'].mean() < 0.4:
            recommendations.append(
                "⚡ Visibilité globale faible. Audit complet ATOMIC-GSO© recommandé. "
                "Contact expert: +352 20 33 81 90"
            )
        
        return recommendations
    
    def _generate_report(self, analysis: Dict, results: List[CitationResult]):
        """Génération rapport visuel"""
        console.print("\n" + "="*60)
        console.print("[bold cyan]📊 RAPPORT MONITORING GSO[/bold cyan]")
        console.print("="*60)
        
        # Score global
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Métrique", style="dim")
        table.add_column("Valeur", justify="right")
        
        table.add_row("Score Global", f"{analysis['global_score']}/{analysis['max_possible_score']}")
        table.add_row("Visibilité IA", f"{analysis['visibility_percentage']}%")
        table.add_row("Citations trouvées", f"{analysis['citations_found']}/{analysis['total_tests']}")
        table.add_row("Taux de citation", f"{analysis['citation_rate']}%")
        table.add_row("Position moyenne", f"{analysis.get('average_position', 'N/A')}")
        
        console.print(table)
        
        # Performance par plateforme
        console.print("\n[bold yellow]📱 Performance par plateforme[/bold yellow]")
        platform_table = Table(show_header=True, header_style="bold blue")
        platform_table.add_column("Plateforme")
        platform_table.add_column("Score Total", justify="right")
        platform_table.add_column("Taux Citation", justify="right")
        platform_table.add_column("Position Moy.", justify="right")
        
        for platform, stats in analysis['platform_performance'].items():
            platform_table.add_row(
                platform,
                str(int(stats['score'])),
                f"{stats['found']*100:.1f}%",
                f"{stats['position']:.1f}" if stats['position'] > 0 else "N/A"
            )
        
        console.print(platform_table)
        
        # Recommandations
        console.print("\n[bold green]💡 Recommandations ATOMIC-GSO©[/bold green]")
        for i, rec in enumerate(analysis['recommendations'], 1):
            console.print(f"{i}. {rec}")
        
        console.print("\n[bold cyan]📞 Support Expert GSO[/bold cyan]")
        console.print("📧 contact@seo-ia.lu | 📱 +352 20 33 81 90")
        console.print("🌐 https://seo-ia.lu/audit-gratuit")
        
    def _save_results(self, results: List[CitationResult]):
        """Sauvegarde résultats pour historique"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gso_results_{self.domain}_{timestamp}.json"
        
        data = {
            "domain": self.domain,
            "timestamp": timestamp,
            "results": [
                {
                    "platform": r.platform,
                    "query": r.query,
                    "position": r.position,
                    "score": r.score,
                    "content_snippet": r.content_snippet,
                    "url": r.url,
                    "timestamp": r.timestamp.isoformat()
                } for r in results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        console.print(f"\n💾 Résultats sauvegardés: {filename}")

async def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GSO Citation Monitor - Expert Sebastien Poletto")
    parser.add_argument("--domain", required=True, help="Domaine à monitorer")
    parser.add_argument("--queries", help="Fichier JSON avec requêtes test")
    parser.add_argument("--config", help="Fichier configuration")
    
    args = parser.parse_args()
    
    # Requêtes par défaut si pas de fichier
    default_queries = [
        "expert GSO Luxembourg",
        "optimisation ChatGPT",
        "référencement intelligence artificielle",
        "consultant SEO IA",
        "audit GSO gratuit"
    ]
    
    queries = default_queries
    if args.queries:
        with open(args.queries, 'r', encoding='utf-8') as f:
            data = json.load(f)
            queries = data.get('queries', default_queries)
    
    # Initialisation moniteur
    monitor = GSACitationMonitor(args.domain, args.config)
    
    # Exécution monitoring
    results = await monitor.run_full_monitoring(queries)
    
    console.print(f"\n✅ Monitoring terminé pour {args.domain}")
    console.print(f"📊 Score global: {results['global_score']}")
    console.print(f"📈 Visibilité IA: {results['visibility_percentage']}%")

if __name__ == "__main__":
    asyncio.run(main())