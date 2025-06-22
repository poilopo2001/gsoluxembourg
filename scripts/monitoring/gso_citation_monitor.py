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
import sys
import os

# Ajoute le chemin parent pour importer modules locaux
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import track

# Import modules GSO
from config.gso_config import config as gso_config
from utils.api_clients import AISearchManager, SearchResult

console = Console()

# Utilise SearchResult de api_clients au lieu de CitationResult
    
class GSACitationMonitor:
    """
    Moniteur citations GSO - Méthodologie ATOMIC-GSO©
    
    Surveillance automatisée de la visibilité dans :
    - ChatGPT Search
    - Perplexity AI  
    - Google AI Overviews
    - Claude AI (via API)
    """
    
    def __init__(self, domain: str, config_path: str = None) -> None:
        self.domain = domain
        self.config = gso_config  # Utilise config globale
        self.results_history = []
        self.setup_logging()
        
        # Initialise gestionnaire API
        demo_mode = os.getenv('GSO_MODE', 'demo') == 'demo'
        self.api_manager = AISearchManager(demo_mode=demo_mode)
        
    def setup_logging(self) -> None:
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
        
    def _get_scoring_config(self) -> Dict[str, int]:
        """Récupère config scoring depuis config globale"""
        return self.config.scoring['citation_positions']
    
    async def test_chatgpt_visibility(self, queries: List[str]) -> List[SearchResult]:
        """
        Test visibilité ChatGPT - Méthode FLIP©
        F.L.I.P = Format, Links, Intent, Position
        """
        results = []
        console.print("[bold blue]🤖 Test ChatGPT Search...[/bold blue]")
        
        for query in track(queries, description="Analyse ChatGPT"):
            try:
                # Utilise API client réel
                platform_results = await self.api_manager.search_all_platforms(
                    query=query,
                    domain=self.domain,
                    platforms=['chatgpt']
                )
                
                if 'chatgpt' in platform_results and platform_results['chatgpt']:
                    results.extend(platform_results['chatgpt'])
                
                # Délai entre requêtes (respect rate limits)
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur ChatGPT pour '{query}': {e}")
                
        return results
    
    async def test_perplexity_visibility(self, queries: List[str]) -> List[SearchResult]:
        """Test visibilité Perplexity AI"""
        results = []
        console.print("[bold green]🔍 Test Perplexity AI...[/bold green]")
        
        for query in track(queries, description="Analyse Perplexity"):
            try:
                platform_results = await self.api_manager.search_all_platforms(
                    query=query,
                    domain=self.domain,
                    platforms=['perplexity']
                )
                
                if 'perplexity' in platform_results and platform_results['perplexity']:
                    results.extend(platform_results['perplexity'])
                    
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur Perplexity pour '{query}': {e}")
                
        return results
    
    async def test_google_ai_visibility(self, queries: List[str]) -> List[SearchResult]:
        """Test visibilité Google AI Overviews"""
        results = []
        console.print("[bold yellow]🔍 Test Google AI Overviews...[/bold yellow]")
        
        for query in track(queries, description="Analyse Google AI"):
            try:
                platform_results = await self.api_manager.search_all_platforms(
                    query=query,
                    domain=self.domain,
                    platforms=['google_ai']
                )
                
                if 'google_ai' in platform_results and platform_results['google_ai']:
                    results.extend(platform_results['google_ai'])
                    
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur Google AI pour '{query}': {e}")
                
        return results
    
    async def test_claude_visibility(self, queries: List[str]) -> List[SearchResult]:
        """Test visibilité Claude AI"""
        results = []
        console.print("[bold purple]🤖 Test Claude AI...[/bold purple]")
        
        for query in track(queries, description="Analyse Claude"):
            try:
                platform_results = await self.api_manager.search_all_platforms(
                    query=query,
                    domain=self.domain,
                    platforms=['claude']
                )
                
                if 'claude' in platform_results and platform_results['claude']:
                    results.extend(platform_results['claude'])
                    
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Erreur Claude pour '{query}': {e}")
                
        return results
    
    # Méthodes _simulate_* supprimées - utilise maintenant api_clients
    
    def _calculate_position_score(self, position: int) -> float:
        """Calcul score selon position - Méthodologie ATOMIC-GSO©"""
        scoring = self._get_scoring_config()
        
        if position == 1:
            return float(scoring["first"])
        elif position <= 3:
            return float(scoring["top_3"])
        elif position <= 5:
            return float(scoring["top_5"])
        elif position > 5:
            return float(scoring["mentioned"])
        else:
            return float(scoring["not_found"])
    
    async def run_full_monitoring(self, queries: List[str]) -> Dict:
        """Exécution monitoring complet - Framework ATOMIC-GSO©"""
        console.print(f"\n[bold cyan]🚀 Début monitoring GSO pour {self.domain}[/bold cyan]")
        console.print(f"📊 {len(queries)} requêtes à tester")
        console.print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        all_results = []
        
        # Test sur toutes les plateformes
        platforms_enabled = []
        for platform_name, platform_config in self.config.platforms.items():
            if platform_config.enabled:
                platforms_enabled.append(platform_name)
        
        # Recherche multi-plateformes optimisée
        if platforms_enabled:
            console.print(f"[bold cyan]🚀 Test sur {len(platforms_enabled)} plateformes activées[/bold cyan]")
            
            for query in queries:
                try:
                    results = await self.api_manager.search_all_platforms(
                        query=query,
                        domain=self.domain,
                        platforms=platforms_enabled
                    )
                    
                    # Collecte résultats de toutes plateformes
                    for platform, platform_results in results.items():
                        all_results.extend(platform_results)
                    
                    # Délai entre requêtes
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Erreur recherche multi-plateformes pour '{query}': {e}")
        
        # Calcul scores et métriques
        analysis = self._analyze_results(all_results)
        
        # Génération rapport
        self._generate_report(analysis, all_results)
        
        # Sauvegarde historique
        self._save_results(all_results)
        
        return analysis
    
    def _analyze_results(self, results: List[SearchResult]) -> Dict:
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
                'found': r.position > 0,
                'snippet': r.snippet
            } for r in results
        ])
        
        # Métriques globales
        total_score = df['score'].sum()
        scoring_config = self._get_scoring_config()
        max_possible = len(results) * scoring_config["first"]
        visibility_percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
        
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
    
    def _generate_report(self, analysis: Dict, results: List[SearchResult]):
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
        console.print(f"📧 {self.config.expert.email} | 📱 {self.config.expert.phone}")
        console.print(f"🌐 {self.config.expert.website}/audit-gratuit")
        
        # Affiche mode démo si activé
        demo_status = self.api_manager.get_demo_mode_status()
        if any(demo_status.values()):
            console.print("\n[yellow]⚠️ Mode démo activé pour certaines plateformes[/yellow]")
            for platform, is_demo in demo_status.items():
                if is_demo:
                    console.print(f"  - {platform}: Mode démo (configurez API key pour résultats réels)")
        
    def _save_results(self, results: List[SearchResult]):
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
                    "content_snippet": r.snippet,
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