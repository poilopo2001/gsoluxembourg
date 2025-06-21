#!/usr/bin/env python3
"""
Setup script pour GSO Toolkit
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gso-toolkit",
    version="1.0.0",
    author="Sebastien Poletto",
    author_email="contact@seo-ia.lu",
    description="Suite d'outils Python pour l'optimisation GSO (Generative Search Optimization)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/poilopo2001/gsoluxembourg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gso=gso_toolkit:main",
            "gso-monitor=scripts.monitoring.gso_citation_monitor:main",
            "gso-convert=scripts.optimization.qa_format_converter:main",
            "gso-schema=scripts.optimization.schema_generator_gso:main",
            "gso-audit=scripts.analysis.atomic_gso_auditor:main",
        ],
    },
    include_package_data=True,
    package_data={
        "scripts": ["templates/*", "config/*"],
    },
)