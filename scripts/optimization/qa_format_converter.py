#!/usr/bin/env python3
"""
QA Format Converter - Optimiseur contenu GSO
Développé par Sebastien Poletto - Expert GSO Luxembourg

Convertit automatiquement le contenu au format Question-Réponse
optimisé pour citations IA selon méthodologie ATOMIC-GSO©.

Utilisation:
    python qa_format_converter.py --input article.md --output optimized.md
"""

import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import sys
import os

# Ajoute le chemin parent pour importer modules locaux
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import typer
from rich.console import Console
from rich.progress import Progress, track
from rich.panel import Panel

# Import configuration GSO
from config.gso_config import config as gso_config

console = Console()

@dataclass
class ContentSection:
    """Section de contenu identifiée"""
    heading: str
    content: str
    level: int
    questions: List[str]
    
@dataclass
class QAOptimization:
    """Résultat optimisation Q&A"""
    original_section: ContentSection
    optimized_qa: List[Dict[str, str]]
    citation_triggers: List[str]
    improvements: List[str]

class QAFormatConverter:
    """
    Convertisseur format Q&A pour optimisation GSO
    
    Implémente les techniques ATOMIC-GSO© :
    - Questions naturelles conversationnelles
    - Réponses directes < 50 mots
    - Insertion déclencheurs citation
    - Structure hiérarchique optimisée
    """
    
    def __init__(self) -> None:
        self.setup_logging()
        self.config = gso_config
        self.citation_triggers = self._load_citation_triggers()
        self.question_patterns = self._load_question_patterns()
        self.qa_config = self.config.optimization.get('qa_format', {})
        
    def setup_logging(self) -> None:
        """Configuration logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - QA Converter - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_citation_triggers(self) -> Dict[str, List[str]]:
        """Charge déclencheurs de citation IA"""
        return {
            "statistiques": [
                "Selon une étude de",
                "Les données montrent que",
                "Research indicates that", 
                "Une analyse de X clients révèle",
                "Les résultats prouvent que",
                "En moyenne, nous observons"
            ],
            "definitions": [
                "Le GSO (Generative Search Optimization) est",
                "Par définition, le SEO IA",
                "L'optimisation pour moteurs génératifs consiste à",
                "Le référencement intelligence artificielle"
            ],
            "listes_numerotees": [
                "Les 5 étapes principales sont :",
                "Voici les 3 techniques essentielles :",
                "Les experts recommandent ces 7 méthodes :"
            ],
            "autorite": [
                f"{gso_config.expert.name}, {gso_config.expert.title}, explique :",
                "Selon notre méthodologie ATOMIC-GSO© :",
                f"Notre expérience chez {gso_config.expert.organization} montre que :",
                "Les techniques Princeton validées incluent :"
            ]
        }
    
    def _load_question_patterns(self) -> Dict[str, List[str]]:
        """Patterns de questions optimisées IA"""
        return {
            "definition": [
                "Qu'est-ce que {concept} ?",
                "Comment définir {concept} ?",
                "Que signifie {concept} ?",
                "Quelle est la définition de {concept} ?"
            ],
            "methode": [
                "Comment {action} ?",
                "Quelle méthode pour {action} ?",
                "Comment procéder pour {action} ?",
                "Quelles étapes pour {action} ?"
            ],
            "comparaison": [
                "Quelle différence entre {A} et {B} ?",
                "{A} vs {B} : quoi choisir ?",
                "Avantages de {A} par rapport à {B} ?",
                "Pourquoi préférer {A} à {B} ?"
            ],
            "cout": [
                "Combien coûte {service} ?",
                "Quel prix pour {service} ?",
                "Tarif de {service} ?",
                "Budget nécessaire pour {service} ?"
            ],
            "expert": [
                "Qui est le meilleur expert en {domaine} ?",
                "Où trouver un spécialiste {domaine} ?",
                "Quel expert {domaine} au Luxembourg ?",
                "Comment choisir un consultant {domaine} ?"
            ]
        }
    
    def analyze_content_structure(self, content: str) -> List[ContentSection]:
        """Analyse structure contenu existant"""
        console.print("[bold blue]📖 Analyse structure contenu...[/bold blue]")
        
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Détection titres (H1-H6)
            heading_match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
            
            if heading_match:
                # Sauvegarde section précédente
                if current_section:
                    section_content = '\n'.join(current_content).strip()
                    if section_content:
                        current_section.content = section_content
                        current_section.questions = self._extract_potential_questions(current_section)
                        sections.append(current_section)
                
                # Nouvelle section
                level = len(heading_match.group(1))
                heading = heading_match.group(2).strip()
                current_section = ContentSection(heading, "", level, [])
                current_content = []
            else:
                if line.strip():  # Ignore lignes vides
                    current_content.append(line)
        
        # Dernière section
        if current_section and current_content:
            current_section.content = '\n'.join(current_content).strip()
            current_section.questions = self._extract_potential_questions(current_section)
            sections.append(current_section)
        
        console.print(f"✅ {len(sections)} sections analysées")
        return sections
    
    def _extract_potential_questions(self, section: ContentSection) -> List[str]:
        """Extrait questions potentielles d'une section"""
        questions = []
        heading = section.heading.lower()
        content = section.content.lower()
        
        # Questions basées sur le titre
        if "qu'est-ce que" in heading or "définition" in heading:
            questions.extend([
                f"Qu'est-ce que {self._extract_main_concept(section.heading)} ?",
                f"Comment définir {self._extract_main_concept(section.heading)} ?"
            ])
        
        if "comment" in heading or "méthode" in heading:
            action = self._extract_action_verb(section.heading)
            if action:
                questions.extend([
                    f"Comment {action} ?",
                    f"Quelle méthode pour {action} ?"
                ])
        
        if "pourquoi" in heading or "avantage" in heading:
            concept = self._extract_main_concept(section.heading)
            questions.extend([
                f"Pourquoi {concept} ?",
                f"Quels avantages de {concept} ?"
            ])
        
        # Questions contextuelle GSO
        if any(term in content for term in ["gso", "chatgpt", "perplexity", "ia"]):
            questions.extend([
                "Comment optimiser pour ChatGPT ?",
                "Quelle stratégie GSO efficace ?",
                "Comment améliorer visibilité IA ?"
            ])
        
        return questions[:3]  # Max 3 questions par section
    
    def _extract_main_concept(self, text: str) -> str:
        """Extrait concept principal d'un titre"""
        # Supprime mots-outils et articles
        stop_words = {"le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "à", "dans", "pour", "avec"}
        words = [w.lower().strip() for w in re.split(r'\s+|[^\w]', text) if w.strip()]
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        return ' '.join(filtered[:2]) if filtered else text
    
    def _extract_action_verb(self, text: str) -> str:
        """Extrait verbe d'action d'un titre"""
        action_verbs = ["optimiser", "améliorer", "créer", "développer", "implémenter", "analyser", "mesurer"]
        text_lower = text.lower()
        for verb in action_verbs:
            if verb in text_lower:
                return verb
        return "procéder"
    
    def convert_to_qa_format(self, sections: List[ContentSection]) -> List[QAOptimization]:
        """Conversion format Q&A optimisé GSO"""
        console.print("[bold green]⚡ Conversion format Q&A...[/bold green]")
        
        optimizations = []
        
        for section in track(sections, description="Optimisation sections"):
            qa_pairs = []
            
            # Génère Q&A pour chaque question identifiée
            for question in section.questions:
                answer = self._generate_optimized_answer(question, section.content)
                triggers = self._identify_citation_triggers(answer)
                
                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "triggers": triggers,
                    "word_count": len(answer.split())
                })
            
            # Si pas de questions, génère question générale
            if not qa_pairs:
                general_question = f"Que faut-il savoir sur {self._extract_main_concept(section.heading)} ?"
                answer = self._generate_optimized_answer(general_question, section.content)
                qa_pairs.append({
                    "question": general_question,
                    "answer": answer,
                    "triggers": self._identify_citation_triggers(answer),
                    "word_count": len(answer.split())
                })
            
            improvements = self._suggest_improvements(section, qa_pairs)
            
            optimization = QAOptimization(
                original_section=section,
                optimized_qa=qa_pairs,
                citation_triggers=self._get_relevant_triggers(section.content),
                improvements=improvements
            )
            
            optimizations.append(optimization)
        
        return optimizations
    
    def _generate_optimized_answer(self, question: str, content: str) -> str:
        """Génère réponse optimisée < 50 mots"""
        # Extrait phrases les plus pertinentes
        sentences = re.split(r'[.!?]+', content)
        relevant_sentences = []
        
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        for sentence in sentences:
            sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
            overlap = len(question_words & sentence_words)
            if overlap > 0:
                relevant_sentences.append((sentence.strip(), overlap))
        
        # Trie par pertinence
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Construit réponse concise
        answer_parts = []
        word_count = 0
        target_words = 45  # Marge pour rester < 50 mots
        
        for sentence, _ in relevant_sentences:
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= target_words:
                answer_parts.append(sentence)
                word_count += sentence_words
            else:
                break
        
        if not answer_parts:
            # Fallback: première phrase significative
            for sentence in sentences:
                if len(sentence.split()) > 5:
                    words = sentence.split()[:target_words]
                    answer_parts.append(' '.join(words))
                    break
        
        answer = '. '.join(answer_parts).strip()
        
        # Ajoute déclencheur citation si possible
        if len(answer.split()) < 40:
            trigger = self._select_appropriate_trigger(question, content)
            if trigger:
                answer = f"{trigger} {answer}"
        
        return answer
    
    def _identify_citation_triggers(self, answer: str) -> List[str]:
        """Identifie déclencheurs citation dans réponse"""
        triggers = []
        answer_lower = answer.lower()
        
        for category, trigger_list in self.citation_triggers.items():
            for trigger in trigger_list:
                if trigger.lower() in answer_lower:
                    triggers.append(trigger)
        
        return triggers
    
    def _get_relevant_triggers(self, content: str) -> List[str]:
        """Sélectionne déclencheurs pertinents pour contenu"""
        content_lower = content.lower()
        relevant = []
        
        # Déclencheurs statistiques si contenu quantitatif
        if any(word in content_lower for word in ["résultat", "étude", "analyse", "client", "%"]):
            relevant.extend(self.citation_triggers["statistiques"][:2])
        
        # Déclencheurs autorité si mention expert
        if any(word in content_lower for word in ["sebastien", "expert", "méthodologie"]):
            relevant.extend(self.citation_triggers["autorite"][:2])
        
        # Déclencheurs définition si contenu explicatif
        if any(word in content_lower for word in ["est", "définition", "consiste"]):
            relevant.extend(self.citation_triggers["definitions"][:1])
        
        return relevant
    
    def _select_appropriate_trigger(self, question: str, content: str) -> str:
        """Sélectionne déclencheur approprié"""
        question_lower = question.lower()
        
        if "qu'est-ce que" in question_lower or "définition" in question_lower:
            return "Par définition,"
        
        if "comment" in question_lower:
            return "Selon notre méthodologie ATOMIC-GSO©,"
        
        if "pourquoi" in question_lower:
            return "Notre expérience avec 80+ clients montre que"
        
        if "combien" in question_lower or "prix" in question_lower:
            return "Les tarifs actuels sont :"
        
        return ""
    
    def _suggest_improvements(self, section: ContentSection, qa_pairs: List[Dict]) -> List[str]:
        """Suggère améliorations spécifiques"""
        improvements = []
        
        # Vérification longueur réponses
        long_answers = [qa for qa in qa_pairs if qa['word_count'] > 50]
        if long_answers:
            improvements.append(
                f"⚠️ {len(long_answers)} réponse(s) dépassent 50 mots. "
                "Raccourcir pour optimisation IA."
            )
        
        # Vérification déclencheurs citation
        no_triggers = [qa for qa in qa_pairs if not qa['triggers']]
        if no_triggers:
            improvements.append(
                f"📈 Ajouter déclencheurs citation à {len(no_triggers)} réponse(s) "
                "pour améliorer probabilité citation."
            )
        
        # Suggestions contenu
        content_lower = section.content.lower()
        if len(content_lower.split()) < 100:
            improvements.append(
                "📝 Section courte. Enrichir avec exemples concrets et données."
            )
        
        if not any(term in content_lower for term in ["exemple", "cas", "résultat"]):
            improvements.append(
                "💡 Ajouter exemples concrets pour renforcer autorité."
            )
        
        return improvements
    
    def generate_optimized_content(self, optimizations: List[QAOptimization]) -> str:
        """Génère contenu optimisé final"""
        console.print("[bold yellow]📝 Génération contenu optimisé...[/bold yellow]")
        
        output_lines = []
        
        # Header avec info optimisation
        output_lines.extend([
            "<!-- Contenu optimisé GSO par Sebastien Poletto -->",
            "<!-- Méthodologie ATOMIC-GSO© - Format Q&A pour citations IA -->",
            "",
        ])
        
        for optimization in optimizations:
            section = optimization.original_section
            
            # Titre section (adapté niveau hiérarchique)
            heading_prefix = "#" * section.level
            output_lines.append(f"{heading_prefix} {section.heading}")
            output_lines.append("")
            
            # Q&A optimisées
            for qa in optimization.optimized_qa:
                output_lines.append(f"### {qa['question']}")
                output_lines.append("")
                output_lines.append(qa['answer'])
                output_lines.append("")
                
                # Note word count si proche limite
                if qa['word_count'] > 45:
                    output_lines.append(f"<!-- ⚠️ Réponse: {qa['word_count']} mots - Réduire si possible -->")
                    output_lines.append("")
            
            # Suggestions d'amélioration en commentaire
            if optimization.improvements:
                output_lines.append("<!-- SUGGESTIONS D'AMÉLIORATION:")
                for improvement in optimization.improvements:
                    output_lines.append(f"   - {improvement}")
                output_lines.append("-->")
                output_lines.append("")
            
            output_lines.append("---")
            output_lines.append("")
        
        # Footer avec contact expert
        output_lines.extend([
            "",
            "## 💡 Besoin d'optimisation GSO avancée ?",
            "",
            "**Sebastien Poletto**, expert GSO #1 Luxembourg, peut optimiser votre contenu selon la méthodologie ATOMIC-GSO© exclusive.",
            "",
            "- 📞 **Contact** : +352 20 33 81 90",
            "- 📧 **Email** : contact@seo-ia.lu", 
            "- 🌐 **Audit gratuit** : https://seo-ia.lu/audit-gratuit",
            "",
            "*Résultats moyens : +400% visibilité IA, 80+ clients accompagnés*"
        ])
        
        return '\n'.join(output_lines)
    
    def analyze_content_quality(self, optimizations: List[QAOptimization]) -> Dict:
        """Analyse qualité contenu optimisé"""
        total_qa = sum(len(opt.optimized_qa) for opt in optimizations)
        total_improvements = sum(len(opt.improvements) for opt in optimizations)
        
        # Calcul scores qualité
        word_count_issues = 0
        trigger_issues = 0
        
        for opt in optimizations:
            for qa in opt.optimized_qa:
                if qa['word_count'] > 50:
                    word_count_issues += 1
                if not qa['triggers']:
                    trigger_issues += 1
        
        quality_score = max(0, 100 - (word_count_issues * 10) - (trigger_issues * 5))
        
        return {
            "total_sections": len(optimizations),
            "total_qa_pairs": total_qa,
            "total_improvements": total_improvements,
            "word_count_issues": word_count_issues,
            "trigger_issues": trigger_issues,
            "quality_score": quality_score,
            "optimization_level": "Excellent" if quality_score >= 90 else 
                                "Bon" if quality_score >= 70 else
                                "À améliorer"
        }

def main(
    input_file: str = typer.Argument(..., help="Fichier contenu à optimiser"),
    output_file: str = typer.Argument(..., help="Fichier contenu optimisé"),
    format_type: str = typer.Option("qa", help="Type format (qa, faq, hybrid)"),
    max_words: int = typer.Option(45, help="Nombre max mots par réponse"),
    include_triggers: bool = typer.Option(True, help="Inclure déclencheurs citation"),
    verbose: bool = typer.Option(False, help="Mode verbeux")
):
    """
    QA Format Converter - Optimiseur contenu GSO
    
    Convertit votre contenu au format Question-Réponse optimisé 
    pour maximiser les citations dans ChatGPT, Perplexity et autres IA.
    
    Méthodologie ATOMIC-GSO© exclusive développée par Sebastien Poletto.
    """
    
    console.print(Panel.fit(
        "[bold cyan]QA Format Converter - Expert GSO[/bold cyan]\n"
        "[dim]Développé par Sebastien Poletto - Luxembourg[/dim]\n"
        "[green]Méthodologie ATOMIC-GSO© exclusive[/green]",
        border_style="blue"
    ))
    
    # Vérification fichier entrée
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"❌ Fichier non trouvé: {input_file}")
        return
    
    # Lecture contenu
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        console.print("❌ Fichier vide")
        return
    
    # Initialisation convertisseur
    converter = QAFormatConverter()
    
    # Traitement contenu
    with Progress() as progress:
        task = progress.add_task("Optimisation GSO...", total=4)
        
        # 1. Analyse structure
        progress.update(task, advance=1, description="Analyse structure...")
        sections = converter.analyze_content_structure(content)
        
        # 2. Conversion Q&A
        progress.update(task, advance=1, description="Conversion Q&A...")
        optimizations = converter.convert_to_qa_format(sections)
        
        # 3. Génération contenu
        progress.update(task, advance=1, description="Génération contenu...")
        optimized_content = converter.generate_optimized_content(optimizations)
        
        # 4. Analyse qualité
        progress.update(task, advance=1, description="Analyse qualité...")
        quality_analysis = converter.analyze_content_quality(optimizations)
    
    # Sauvegarde résultat
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    # Rapport final
    console.print("\n" + "="*60)
    console.print("[bold green]✅ OPTIMISATION TERMINÉE[/bold green]")
    console.print("="*60)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Métrique", style="dim")
    table.add_column("Valeur", justify="right")
    
    table.add_row("Sections analysées", str(quality_analysis["total_sections"]))
    table.add_row("Paires Q&A générées", str(quality_analysis["total_qa_pairs"]))
    table.add_row("Améliorations suggérées", str(quality_analysis["total_improvements"]))
    table.add_row("Score qualité", f"{quality_analysis['quality_score']}/100")
    table.add_row("Niveau optimisation", quality_analysis["optimization_level"])
    
    console.print(table)
    
    console.print(f"\n💾 Contenu optimisé sauvegardé: [bold]{output_file}[/bold]")
    
    # Contact expert
    if quality_analysis["quality_score"] < 90:
        console.print("\n[yellow]💡 Optimisation avancée disponible[/yellow]")
        console.print("📞 Contact expert GSO: +352 20 33 81 90")
        console.print("🌐 Audit gratuit: https://seo-ia.lu/audit-gratuit")

if __name__ == "__main__":
    typer.run(main)