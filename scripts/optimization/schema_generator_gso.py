#!/usr/bin/env python3
"""
Schema.org Generator GSO - Générateur Schema optimisé LLMs
Développé par Sebastien Poletto - Expert GSO Luxembourg

Génère automatiquement le markup Schema.org optimisé pour 
citations IA selon les standards ATOMIC-GSO©.

Utilisation:
    python schema_generator_gso.py --type article --title "Mon Article" --output schema.json
"""

import json
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin
import sys
import os

# Ajoute le chemin parent pour importer modules locaux
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Import configuration GSO
from config.gso_config import config as gso_config

console = Console()

@dataclass
class SchemaConfig:
    """Configuration Schema.org"""
    base_url: str
    organization_name: str = None
    organization_url: str = None
    expert_name: str = None
    location: str = None
    phone: str = None
    email: str = None
    logo_url: str = None
    image_url: str = None
    
    def __post_init__(self) -> None:
        """Initialise avec config GSO si valeurs non fournies"""
        if not self.organization_name:
            self.organization_name = gso_config.expert.organization
        if not self.organization_url:
            self.organization_url = gso_config.expert.website
        if not self.expert_name:
            self.expert_name = gso_config.expert.name
        if not self.location:
            self.location = gso_config.expert.location
        if not self.phone:
            self.phone = gso_config.expert.phone
        if not self.email:
            self.email = gso_config.expert.email
        if not self.logo_url:
            self.logo_url = f"{gso_config.expert.website}/logo.png"
        if not self.image_url:
            self.image_url = f"{gso_config.expert.website}/seo-ia-headshot.png"

class SchemaGeneratorGSO:
    """
    Générateur Schema.org optimisé pour GSO
    
    Implémente les standards ATOMIC-GSO© pour :
    - Articles et contenus
    - Pages services
    - Profils experts
    - FAQ optimisées
    - Organisations
    """
    
    def __init__(self, config: SchemaConfig) -> None:
        self.config = config
        self.gso_extensions = self._load_gso_extensions()
        
    def _load_gso_extensions(self) -> Dict[str, List[str]]:
        """Extensions Schema.org spécifiques GSO"""
        return {
            "gso_authority_signals": [
                "expert_credentials",
                "methodology_name", 
                "client_count",
                "satisfaction_rating",
                "years_experience",
                "specialization_areas"
            ],
            "llm_optimization_properties": [
                "direct_answer_format",
                "citation_triggers",
                "context_clarity",
                "authority_markers",
                "structured_data"
            ],
            "platform_specific": {
                "chatgpt": {
                    "focus": "concise_answers",
                    "format": "question_answer_pairs",
                    "context": "expert_authority"
                },
                "perplexity": {
                    "focus": "source_credibility", 
                    "format": "structured_facts",
                    "context": "research_depth"
                },
                "google_ai": {
                    "focus": "snippet_optimization",
                    "format": "featured_snippet_ready",
                    "context": "search_intent_match"
                }
            }
        }
    
    def generate_article_schema(
        self, 
        title: str,
        content: str,
        url: str,
        author: str = None,
        published_date: str = None,
        modified_date: str = None,
        image_url: str = None,
        keywords: List[str] = None,
        category: str = None
    ) -> Dict:
        """Génère Schema Article optimisé GSO"""
        
        author_name = author or self.config.expert_name
        pub_date = published_date or datetime.now().isoformat()
        mod_date = modified_date or datetime.now().isoformat()
        article_image = image_url or self.config.image_url
        
        # Extraction automatique informations contenu
        word_count = len(content.split())
        reading_time = f"PT{max(1, word_count // 200)}M"
        
        # Détection FAQ dans contenu
        faq_items = self._extract_faq_from_content(content)
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": self._generate_description(content),
            "image": {
                "@type": "ImageObject",
                "url": article_image,
                "width": 1200,
                "height": 630
            },
            "url": urljoin(self.config.base_url, url),
            "datePublished": pub_date,
            "dateModified": mod_date,
            "author": {
                "@type": "Person",
                "name": author_name,
                "jobTitle": "Expert GSO/GEO",
                "url": self.config.organization_url,
                "image": self.config.image_url,
                "sameAs": [
                    self.config.organization_url,
                    f"{self.config.organization_url}/expert-gso"
                ],
                "knowsAbout": [
                    "Generative Search Optimization",
                    "ChatGPT Optimization", 
                    "Perplexity SEO",
                    "Google AI Overviews",
                    "Claude AI Optimization",
                    "SEO IA",
                    "Référencement Intelligence Artificielle",
                    "ATOMIC-GSO Methodology"
                ]
            },
            "publisher": {
                "@type": "Organization",
                "name": self.config.organization_name,
                "url": self.config.organization_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": self.config.logo_url
                },
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": self.config.phone,
                    "contactType": "Customer Service",
                    "availableLanguage": ["French", "English", "German"]
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": urljoin(self.config.base_url, url)
            },
            "wordCount": word_count,
            "timeRequired": reading_time,
            "inLanguage": "fr-FR",
            "isAccessibleForFree": True,
            "isPartOf": {
                "@type": "WebSite",
                "@id": self.config.base_url
            }
        }
        
        # Ajout catégorie si fournie
        if category:
            schema["articleSection"] = category
            
        # Ajout mots-clés si fournis
        if keywords:
            schema["keywords"] = keywords
            
        # Ajout FAQ si détectée
        if faq_items:
            schema["mainEntity"] = {
                "@type": "FAQPage",
                "mainEntity": faq_items
            }
        
        # Extensions GSO spécifiques
        schema.update(self._add_gso_extensions("article", content))
        
        return schema
    
    def generate_service_schema(
        self,
        service_name: str,
        description: str,
        url: str,
        price_range: str = None,
        duration: str = None,
        includes: List[str] = None
    ) -> Dict:
        """Génère Schema Service optimisé GSO"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": service_name,
            "description": description,
            "url": urljoin(self.config.base_url, url),
            "provider": {
                "@type": "Person",
                "name": self.config.expert_name,
                "jobTitle": "Expert GSO Luxembourg",
                "url": self.config.organization_url,
                "image": self.config.image_url,
                "telephone": self.config.phone,
                "email": self.config.email,
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "LU",
                    "addressLocality": "Luxembourg City"
                }
            },
            "areaServed": {
                "@type": "Country", 
                "name": "Luxembourg"
            },
            "availableLanguage": ["French", "English", "German"],
            "serviceType": "Digital Marketing Consultation",
            "category": "SEO IA / GSO Optimization"
        }
        
        # Prix si fourni
        if price_range:
            schema["offers"] = {
                "@type": "Offer",
                "priceRange": price_range,
                "priceCurrency": "EUR",
                "availability": "https://schema.org/InStock",
                "validFrom": datetime.now().isoformat()
            }
        
        # Durée si fournie
        if duration:
            schema["duration"] = duration
            
        # Inclusions si fournies
        if includes:
            schema["serviceOutput"] = includes
        
        # Ajout avis/témoignages
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": 4.9,
            "reviewCount": 80,
            "bestRating": 5
        }
        
        return schema
    
    def generate_expert_profile_schema(
        self,
        name: str = None,
        bio: str = None,
        url: str = None,
        specializations: List[str] = None
    ) -> Dict:
        """Génère Schema Profil Expert optimisé"""
        
        expert_name = name or self.config.expert_name
        profile_url = url or "/expert-gso"
        
        default_specializations = [
            "Generative Search Optimization (GSO)",
            "Generative Engine Optimization (GEO)", 
            "SEO Intelligence Artificielle",
            "Optimisation ChatGPT",
            "Optimisation Perplexity",
            "Google AI Overviews",
            "Claude AI Optimization",
            "Référencement Conversationnel",
            "ATOMIC-GSO Methodology",
            "Formation GSO"
        ]
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": expert_name,
            "jobTitle": "Expert GSO/GEO #1 Luxembourg",
            "description": bio or "Expert GSO Luxembourg spécialisé en optimisation pour moteurs génératifs. Créateur méthodologie ATOMIC-GSO©. +400% visibilité IA garantie.",
            "url": urljoin(self.config.base_url, profile_url),
            "image": self.config.image_url,
            "telephone": self.config.phone,
            "email": self.config.email,
            "worksFor": {
                "@type": "Organization",
                "name": self.config.organization_name,
                "url": self.config.organization_url
            },
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "LU",
                "addressLocality": "Luxembourg City"
            },
            "knowsAbout": specializations or default_specializations,
            "hasCredential": [
                {
                    "@type": "EducationalOccupationalCredential",
                    "name": "Expert GSO Certifié",
                    "credentialCategory": "Professional Certification"
                },
                {
                    "@type": "EducationalOccupationalCredential", 
                    "name": "Créateur Méthodologie ATOMIC-GSO©",
                    "credentialCategory": "Proprietary Methodology"
                }
            ],
            "award": [
                "Expert GSO #1 Luxembourg 2024",
                "Pionnier GSO Luxembourg",
                "4.9/5 Satisfaction Client (80+ avis)"
            ],
            "memberOf": {
                "@type": "ProfessionalService",
                "name": "Expert GSO Luxembourg"
            }
        }
        
        # Statistiques performance
        schema["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Services GSO Expert",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "name": "Audit GSO Gratuit",
                    "description": "Analyse complète visibilité IA",
                    "price": "0",
                    "priceCurrency": "EUR"
                },
                {
                    "@type": "Offer", 
                    "name": "Optimisation ChatGPT",
                    "description": "+600% visibilité moyenne",
                    "priceRange": "8000-25000",
                    "priceCurrency": "EUR"
                }
            ]
        }
        
        return schema
    
    def generate_faq_schema(self, qa_pairs: List[Dict[str, str]]) -> Dict:
        """Génère Schema FAQ optimisé LLMs"""
        
        faq_items = []
        
        for qa in qa_pairs:
            question = qa.get("question", "")
            answer = qa.get("answer", "")
            
            # Optimisation réponse pour LLMs
            optimized_answer = self._optimize_answer_for_llms(answer)
            
            faq_item = {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": optimized_answer,
                    "author": {
                        "@type": "Person",
                        "name": self.config.expert_name,
                        "jobTitle": "Expert GSO Luxembourg"
                    }
                }
            }
            
            faq_items.append(faq_item)
        
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items,
            "about": {
                "@type": "Thing",
                "name": "GSO - Generative Search Optimization"
            },
            "audience": {
                "@type": "Audience",
                "audienceType": "Business Professionals"
            },
            "publisher": {
                "@type": "Organization",
                "name": self.config.organization_name,
                "url": self.config.organization_url
            }
        }
        
        return schema
    
    def generate_organization_schema(self) -> Dict:
        """Génère Schema Organisation optimisé"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": ["Organization", "ProfessionalService"],
            "name": self.config.organization_name,
            "alternateName": "SEO IA Luxembourg",
            "url": self.config.organization_url,
            "logo": self.config.logo_url,
            "image": self.config.image_url,
            "description": "Expert GSO Luxembourg #1. Optimisation moteurs génératifs (ChatGPT, Perplexity, Google AI). Méthodologie ATOMIC-GSO© exclusive. +400% visibilité IA garantie.",
            "telephone": self.config.phone,
            "email": self.config.email,
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "LU",
                "addressLocality": "Luxembourg City"
            },
            "areaServed": {
                "@type": "Country",
                "name": "Luxembourg"
            },
            "founder": {
                "@type": "Person",
                "name": self.config.expert_name,
                "jobTitle": "Expert GSO/GEO"
            },
            "employee": {
                "@type": "Person", 
                "name": self.config.expert_name,
                "jobTitle": "Expert GSO/GEO Luxembourg"
            },
            "serviceType": [
                "Generative Search Optimization",
                "SEO Intelligence Artificielle",
                "Optimisation ChatGPT",
                "Formation GSO"
            ],
            "priceRange": "€€€",
            "paymentAccepted": ["Cash", "Credit Card", "Bank Transfer"],
            "currenciesAccepted": "EUR",
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": 4.9,
                "reviewCount": 80,
                "bestRating": 5
            },
            "review": [
                {
                    "@type": "Review",
                    "reviewRating": {
                        "@type": "Rating",
                        "ratingValue": 5
                    },
                    "author": {
                        "@type": "Person",
                        "name": "Client Luxembourg"
                    },
                    "reviewBody": "Résultats exceptionnels. +400% de visibilité IA en 3 mois."
                }
            ],
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "Services GSO",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": "Audit GSO Gratuit",
                            "description": "Analyse complète visibilité IA"
                        }
                    }
                ]
            },
            "sameAs": [
                self.config.organization_url,
                f"{self.config.organization_url}/expert-gso"
            ],
            "knowsAbout": [
                "Generative Search Optimization",
                "ChatGPT Optimization",
                "Perplexity SEO", 
                "Google AI Overviews",
                "Claude AI",
                "SEO IA",
                "Référencement Intelligence Artificielle"
            ]
        }
        
        return schema
    
    def _extract_faq_from_content(self, content: str) -> List[Dict]:
        """Extrait FAQ du contenu"""
        faq_items = []
        
        # Pattern pour détecter Q&A
        qa_pattern = r'(?:^|\n)(?:###?\s*)(.+\?)\s*\n([^#\n]+(?:\n(?!#{1,3}\s)[^#\n]+)*)'
        matches = re.findall(qa_pattern, content, re.MULTILINE)
        
        for question, answer in matches:
            cleaned_answer = re.sub(r'\n+', ' ', answer.strip())
            if len(cleaned_answer) > 10:  # Filtre réponses trop courtes
                faq_items.append({
                    "@type": "Question",
                    "name": question.strip(),
                    "acceptedAnswer": {
                        "@type": "Answer", 
                        "text": cleaned_answer
                    }
                })
        
        return faq_items[:10]  # Max 10 FAQ
    
    def _generate_description(self, content: str, max_length: int = 160) -> str:
        """Génère description optimisée"""
        # Supprime markdown et nettoie
        clean_content = re.sub(r'[#*`\[\]()]', '', content)
        sentences = re.split(r'[.!?]+', clean_content)
        
        description = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(description + sentence) < max_length:
                description += sentence + ". "
            elif len(description) > 50:
                break
        
        return description.strip()
    
    def _optimize_answer_for_llms(self, answer: str) -> str:
        """Optimise réponse pour LLMs"""
        # Limite à 50 mots max
        words = answer.split()
        if len(words) > 50:
            answer = ' '.join(words[:50]) + "..."
        
        # Ajoute contexte expert si absent
        if "sebastien poletto" not in answer.lower() and len(words) < 40:
            answer = f"Selon Sebastien Poletto, expert GSO Luxembourg : {answer}"
        
        return answer
    
    def _add_gso_extensions(self, schema_type: str, content: str = "") -> Dict:
        """Ajoute extensions GSO spécifiques"""
        extensions = {}
        
        # Extensions autorité expert
        if "gso" in content.lower() or "chatgpt" in content.lower():
            extensions["specialty"] = {
                "@type": "Specialty",
                "name": "Generative Search Optimization"
            }
        
        # Métriques performance
        extensions["performanceMetrics"] = {
            "@type": "PropertyValue",
            "name": "Average Visibility Increase",
            "value": "+400%"
        }
        
        return extensions
    
    def validate_schema(self, schema: Dict) -> Dict:
        """Valide schema généré"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Vérifications basiques
        required_fields = ["@context", "@type"]
        for field in required_fields:
            if field not in schema:
                validation_results["errors"].append(f"Champ requis manquant: {field}")
                validation_results["valid"] = False
        
        # Vérifications spécifiques GSO
        if schema.get("@type") == "Article":
            if "author" not in schema:
                validation_results["warnings"].append("Auteur recommandé pour crédibilité")
            
            if "wordCount" not in schema:
                validation_results["suggestions"].append("Ajouter wordCount pour optimisation")
        
        return validation_results
    
    def generate_complete_page_schema(
        self,
        page_type: str,
        **kwargs
    ) -> Dict:
        """Génère schema complet pour page"""
        
        schemas = []
        
        # Schema principal selon type
        if page_type == "article":
            main_schema = self.generate_article_schema(**kwargs)
        elif page_type == "service":
            main_schema = self.generate_service_schema(**kwargs)
        elif page_type == "expert":
            main_schema = self.generate_expert_profile_schema(**kwargs)
        elif page_type == "faq":
            main_schema = self.generate_faq_schema(**kwargs)
        else:
            main_schema = self.generate_organization_schema()
        
        schemas.append(main_schema)
        
        # Toujours ajouter schema organisation
        if page_type != "organization":
            org_schema = self.generate_organization_schema()
            schemas.append(org_schema)
        
        # Schema combiné
        if len(schemas) == 1:
            return schemas[0]
        else:
            return {
                "@context": "https://schema.org",
                "@graph": schemas
            }

def main(
    schema_type: str = typer.Argument(..., help="Type schema (article, service, expert, faq, organization)"),
    title: str = typer.Option(None, help="Titre du contenu"),
    description: str = typer.Option(None, help="Description"),
    url: str = typer.Option("/", help="URL relative"),
    output: str = typer.Option("schema.json", help="Fichier sortie"),
    base_url: str = typer.Option("https://seo-ia.lu", help="URL base site"),
    content_file: str = typer.Option(None, help="Fichier contenu pour analyse"),
    validate: bool = typer.Option(True, help="Valider schema généré"),
    pretty: bool = typer.Option(True, help="Format JSON indenté")
):
    """
    Schema.org Generator GSO - Générateur Schema optimisé LLMs
    
    Génère automatiquement le markup Schema.org optimisé pour 
    citations IA selon méthodologie ATOMIC-GSO©.
    
    Développé par Sebastien Poletto - Expert GSO Luxembourg.
    """
    
    console.print(Panel.fit(
        "[bold cyan]Schema.org Generator GSO[/bold cyan]\n"
        "[dim]Développé par Sebastien Poletto - Luxembourg[/dim]\n"
        "[green]Méthodologie ATOMIC-GSO© exclusive[/green]",
        border_style="blue"
    ))
    
    # Configuration
    config = SchemaConfig(base_url=base_url)
    generator = SchemaGeneratorGSO(config)
    
    # Lecture contenu si fichier fourni
    content = ""
    if content_file and Path(content_file).exists():
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        console.print(f"📖 Contenu lu: {content_file}")
    
    # Génération schema selon type
    try:
        if schema_type == "article":
            if not title:
                title = "Article GSO Expert"
            schema = generator.generate_article_schema(
                title=title,
                content=content,
                url=url,
                description=description
            )
        
        elif schema_type == "service":
            if not title:
                title = "Service GSO Expert"
            schema = generator.generate_service_schema(
                service_name=title,
                description=description or "Service GSO professionnel",
                url=url
            )
        
        elif schema_type == "expert":
            schema = generator.generate_expert_profile_schema(
                name=title,
                bio=description,
                url=url
            )
        
        elif schema_type == "faq":
            # Extraction FAQ du contenu
            qa_pairs = []
            if content:
                # Simple extraction Q&A
                qa_pattern = r'(?:^|\n)(?:###?\s*)(.+\?)\s*\n([^#\n]+(?:\n(?!#{1,3}\s)[^#\n]+)*)'
                matches = re.findall(qa_pattern, content, re.MULTILINE)
                qa_pairs = [{"question": q, "answer": a.strip()} for q, a in matches]
            
            if not qa_pairs:
                qa_pairs = [{"question": "Qu'est-ce que le GSO ?", "answer": "Le GSO est l'optimisation pour moteurs génératifs."}]
            
            schema = generator.generate_faq_schema(qa_pairs)
        
        elif schema_type == "organization":
            schema = generator.generate_organization_schema()
        
        else:
            console.print(f"❌ Type schema non supporté: {schema_type}")
            return
        
        # Validation si demandée
        if validate:
            validation = generator.validate_schema(schema)
            
            if validation["errors"]:
                console.print("[red]❌ Erreurs validation:[/red]")
                for error in validation["errors"]:
                    console.print(f"  • {error}")
            
            if validation["warnings"]:
                console.print("[yellow]⚠️ Avertissements:[/yellow]")
                for warning in validation["warnings"]:
                    console.print(f"  • {warning}")
            
            if validation["suggestions"]:
                console.print("[blue]💡 Suggestions:[/blue]")
                for suggestion in validation["suggestions"]:
                    console.print(f"  • {suggestion}")
        
        # Sauvegarde schema
        output_path = Path(output)
        indent = 2 if pretty else None
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=indent, ensure_ascii=False)
        
        console.print(f"\n✅ Schema généré: [bold]{output}[/bold]")
        
        # Aperçu schema
        if pretty:
            console.print("\n📋 Aperçu Schema:")
            syntax = Syntax(json.dumps(schema, indent=2, ensure_ascii=False)[:1000] + "...", "json")
            console.print(syntax)
        
        # Statistiques
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Propriété", style="dim")
        table.add_column("Valeur", justify="right")
        
        table.add_row("Type Schema", schema.get("@type", "N/A"))
        table.add_row("Taille JSON", f"{len(json.dumps(schema))} caractères")
        table.add_row("Optimisé GSO", "✅ Oui")
        
        if "mainEntity" in schema:
            table.add_row("FAQ Items", str(len(schema["mainEntity"])))
        
        console.print("\n📊 Informations Schema:")
        console.print(table)
        
        # Contact expert
        console.print("\n[cyan]💡 Optimisation avancée Schema.org[/cyan]")
        console.print("📞 Expert GSO: +352 20 33 81 90")
        console.print("🌐 Audit gratuit: https://seo-ia.lu/audit-gratuit")
        
    except Exception as e:
        console.print(f"❌ Erreur génération: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    typer.run(main)