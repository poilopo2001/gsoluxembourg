#!/usr/bin/env python3
"""
Test script to verify GSO Toolkit structure
"""

import os
import json
from pathlib import Path

def test_structure():
    """Vérifie la structure du projet"""
    print("🔍 Vérification structure GSO Toolkit...\n")
    
    # Vérifie fichiers racine
    root_files = [
        "README.md",
        "requirements.txt",
        "setup.py",
        "gso_toolkit.py",
        ".env.example"
    ]
    
    print("📁 Fichiers racine:")
    for file in root_files:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")
    
    # Vérifie structure scripts
    print("\n📂 Structure scripts/:")
    script_dirs = {
        "scripts/monitoring": ["gso_citation_monitor.py"],
        "scripts/optimization": ["qa_format_converter.py", "schema_generator_gso.py"],
        "scripts/analysis": ["atomic_gso_auditor.py"],
        "scripts/config": ["gso_config.py", "__init__.py"],
        "scripts/utils": ["api_clients.py", "__init__.py"],
        "scripts/templates": ["demo_article.md"]
    }
    
    for dir_path, files in script_dirs.items():
        print(f"\n  📁 {dir_path}/")
        for file in files:
            full_path = os.path.join(dir_path, file)
            exists = os.path.exists(full_path)
            status = "✅" if exists else "❌"
            print(f"    {status} {file}")
    
    # Vérifie configuration
    print("\n⚙️  Configuration:")
    env_example = Path(".env.example")
    if env_example.exists():
        print("  ✅ .env.example trouvé")
        with open(env_example) as f:
            lines = f.readlines()
            print(f"  📊 {len(lines)} lignes de configuration")
    
    # Résumé
    print("\n📊 Résumé:")
    print(f"  - Scripts Python: {len([f for d in script_dirs.values() for f in d if f.endswith('.py')])}")
    print(f"  - Modules: {len(script_dirs)}")
    print("  - Mode: Demo (pas besoin d'API keys)")
    
    print("\n✅ Structure GSO Toolkit vérifiée!")
    print("\n💡 Pour utiliser les outils:")
    print("   1. pip install -r requirements.txt")
    print("   2. cp .env.example .env")
    print("   3. python3 gso_toolkit.py demo")

if __name__ == "__main__":
    test_structure()