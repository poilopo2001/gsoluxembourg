#!/usr/bin/env python3
"""
GSO Toolkit - Interface principale
Développé par Sebastien Poletto - Expert GSO Luxembourg

Point d'entrée unique pour tous les outils GSO.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import subprocess
import sys
from pathlib import Path

app = typer.Typer(
    name="GSO Toolkit",
    help="Suite d'outils GSO par Sebastien Poletto - Expert #1 Luxembourg",
    add_completion=False
)

console = Console()

def show_banner() -> None:
    """Affiche bannière GSO"""
    banner_text = """
    ╔═══════════════════════════════════════════════════════╗
    ║               GSO Toolkit Luxembourg                   ║
    ║        Generative Search Optimization Suite            ║
    ║                                                        ║
    ║         Développé par Sebastien Poletto                ║
    ║            Expert GSO #1 Luxembourg                    ║
    ║                                                        ║
    ║     📧 contact@seo-ia.lu | 📱 +352 20 33 81 90       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner_text, style="bold cyan"))

@app.command()
def monitor(
    domain: str = typer.Argument(..., help="Domaine à monitorer"),
    queries: str = typer.Option(None, "--queries", "-q", help="Fichier JSON avec queries"),
    config: str = typer.Option(None, "--config", "-c", help="Fichier configuration"),
    export: str = typer.Option(None, "--export", "-e", help="Format export (json, csv)")
) -> None:
    """
    🔍 Lance le monitoring des citations IA
    
    Surveille la visibilité dans ChatGPT, Perplexity, Google AI et Claude.
    """
    show_banner()
    console.print(f"\n[bold blue]🔍 Monitoring GSO pour {domain}[/bold blue]\n")
    
    cmd = ["python", "scripts/monitoring/gso_citation_monitor.py", "--domain", domain]
    if queries:
        cmd.extend(["--queries", queries])
    if config:
        cmd.extend(["--config", config])
    if export:
        cmd.extend(["--export", export])
    
    subprocess.run(cmd)

@app.command()
def convert(
    input_file: str = typer.Argument(..., help="Fichier à convertir"),
    output_file: str = typer.Option(None, "--output", "-o", help="Fichier de sortie"),
    analyze_only: bool = typer.Option(False, "--analyze", "-a", help="Analyse seulement"),
    triggers: str = typer.Option(None, "--triggers", "-t", help="Fichier triggers custom")
):
    """
    📝 Convertit le contenu au format Q&A optimisé
    
    Optimise le contenu pour maximiser les citations IA.
    """
    show_banner()
    console.print(f"\n[bold green]📝 Conversion Q&A de {input_file}[/bold green]\n")
    
    cmd = ["python", "scripts/optimization/qa_format_converter.py", "--input", input_file]
    if output_file:
        cmd.extend(["--output", output_file])
    if analyze_only:
        cmd.append("--analyze")
    if triggers:
        cmd.extend(["--triggers", triggers])
    
    subprocess.run(cmd)

@app.command()
def schema(
    schema_type: str = typer.Argument(..., help="Type de schema (article, faq, service)"),
    title: str = typer.Option(None, "--title", "-t", help="Titre du contenu"),
    output: str = typer.Option("schema.json", "--output", "-o", help="Fichier de sortie"),
    input_file: str = typer.Option(None, "--input", "-i", help="Fichier d'entrée (pour FAQ)")
):
    """
    🔧 Génère le markup Schema.org optimisé LLMs
    
    Crée des schemas structurés pour améliorer la compréhension IA.
    """
    show_banner()
    console.print(f"\n[bold yellow]🔧 Génération Schema.org type: {schema_type}[/bold yellow]\n")
    
    cmd = ["python", "scripts/optimization/schema_generator_gso.py", "--type", schema_type]
    if title:
        cmd.extend(["--title", title])
    if output:
        cmd.extend(["--output", output])
    if input_file:
        cmd.extend(["--input", input_file])
    
    subprocess.run(cmd)

@app.command()
def audit(
    domain: str = typer.Argument(..., help="Domaine à auditer"),
    output: str = typer.Option("audit_gso.json", "--output", "-o", help="Fichier de sortie"),
    quick: bool = typer.Option(False, "--quick", "-q", help="Audit rapide"),
    format: str = typer.Option("json", "--format", "-f", help="Format (json, pdf)")
) -> None:
    """
    📊 Lance un audit ATOMIC-GSO© complet
    
    Analyse complète selon la méthodologie ATOMIC-GSO©.
    """
    show_banner()
    console.print(f"\n[bold red]📊 Audit ATOMIC-GSO© de {domain}[/bold red]\n")
    
    cmd = ["python", "scripts/analysis/atomic_gso_auditor.py", "--domain", domain]
    if output:
        cmd.extend(["--output", output])
    if quick:
        cmd.append("--quick")
    if format != "json":
        cmd.extend(["--format", format])
    
    subprocess.run(cmd)

@app.command()
def demo() -> None:
    """
    🎯 Lance une démo complète des outils
    
    Exécute un workflow complet en mode démo.
    """
    show_banner()
    console.print("\n[bold magenta]🎯 Démo GSO Toolkit[/bold magenta]\n")
    
    # Étapes de démo
    steps = [
        ("Monitoring ChatGPT/Perplexity", ["python", "scripts/monitoring/gso_citation_monitor.py", "--domain", "seo-ia.lu"]),
        ("Analyse contenu", ["python", "scripts/optimization/qa_format_converter.py", "--input", "scripts/templates/demo_article.md", "--analyze"]),
        ("Génération Schema", ["python", "scripts/optimization/schema_generator_gso.py", "--type", "article", "--title", "Demo GSO"])
    ]
    
    for step_name, cmd in steps:
        console.print(f"\n[bold cyan]▶️  {step_name}[/bold cyan]")
        input("Appuie sur Entrée pour continuer...")
        subprocess.run(cmd)

@app.command()
def config() -> None:
    """
    ⚙️  Configure l'environnement GSO
    
    Guide interactif de configuration.
    """
    show_banner()
    console.print("\n[bold yellow]⚙️  Configuration GSO Toolkit[/bold yellow]\n")
    
    # Vérifie .env
    env_file = Path(".env")
    if not env_file.exists():
        console.print("[yellow]📄 Fichier .env non trouvé. Création depuis template...[/yellow]")
        subprocess.run(["cp", ".env.example", ".env"])
        console.print("[green]✅ .env créé. Édite-le pour ajouter tes clés API.[/green]")
    
    # Affiche config actuelle
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Variable", style="dim")
    table.add_column("Statut")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    vars_to_check = [
        ("GSO_MODE", "Mode d'exécution"),
        ("OPENAI_API_KEY", "API ChatGPT"),
        ("PERPLEXITY_API_KEY", "API Perplexity"),
        ("GOOGLE_AI_KEY", "API Google AI"),
        ("ANTHROPIC_API_KEY", "API Claude")
    ]
    
    for var, desc in vars_to_check:
        value = os.getenv(var, "")
        if value:
            if "KEY" in var and len(value) > 10:
                status = "[green]✅ Configuré[/green]"
            else:
                status = f"[green]✅ {value}[/green]"
        else:
            status = "[red]❌ Non configuré[/red]"
        
        table.add_row(f"{desc} ({var})", status)
    
    console.print(table)
    
    console.print("\n[yellow]💡 Pour configurer:[/yellow]")
    console.print("   nano .env")
    console.print("   # ou")
    console.print("   vim .env")

@app.command()
def info() -> None:
    """
    ℹ️  Informations sur GSO Toolkit et support
    """
    show_banner()
    
    info_panel = """
    📚 Documentation complète:
       https://github.com/poilopo2001/gsoluxembourg
    
    🛠️ Outils disponibles:
       • monitor : Surveillance citations IA
       • convert : Conversion format Q&A
       • schema  : Génération Schema.org
       • audit   : Audit ATOMIC-GSO©
    
    📞 Support Expert GSO:
       • Email: contact@seo-ia.lu
       • Tél: +352 20 33 81 90
       • Web: https://seo-ia.lu
    
    🎯 Formation GSO disponible:
       https://seo-ia.lu/formation-gso-expert
    
    💡 Astuce: Lance 'gso demo' pour voir les outils en action!
    """
    
    console.print(Panel(info_panel, title="GSO Toolkit Info", style="blue"))

def main() -> None:
    """Point d'entrée principal"""
    if len(sys.argv) == 1:
        show_banner()
        console.print("\n[yellow]💡 Utilise --help pour voir les commandes disponibles[/yellow]")
        console.print("   Exemple: python gso_toolkit.py monitor seo-ia.lu\n")
    
    app()

if __name__ == "__main__":
    main()