#!/usr/bin/env python3
"""
Module de validation et sécurisation des entrées
Développé par Sebastien Poletto - Expert GSO Luxembourg

Fournit des validateurs robustes pour sécuriser toutes les entrées utilisateur.
"""

import re
import os
from pathlib import Path
from typing import Any, Optional, Union, List
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator, ValidationError
import ipaddress


class PathValidator(BaseModel):
    """Validateur sécurisé pour les chemins de fichiers"""
    path: str = Field(..., min_length=1, max_length=500)
    
    @field_validator('path', mode='before')
    @classmethod
    def validate_safe_path(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Le chemin doit être une chaîne de caractères")
        
        # Nettoyer les espaces
        value = value.strip()
        
        # Vérifier les caractères dangereux
        dangerous_chars = ['..', '~', '\x00', '\n', '\r', '|', '&', ';', '$', '`', '<', '>']
        for char in dangerous_chars:
            if char in value:
                raise ValueError(f"Caractère non autorisé dans le chemin: {char}")
        
        # Convertir en Path et résoudre
        try:
            path_obj = Path(value).resolve()
            
            # Vérifier que le chemin ne sort pas du répertoire de travail
            cwd = Path.cwd()
            if not (path_obj == cwd or cwd in path_obj.parents or path_obj in cwd.parents):
                # Permettre les chemins dans le home de l'utilisateur
                home = Path.home()
                if not (path_obj == home or home in path_obj.parents or path_obj in home.parents):
                    raise ValueError("Chemin en dehors des répertoires autorisés")
            
            return str(path_obj)
            
        except Exception as e:
            raise ValueError(f"Chemin invalide: {str(e)}")


class DomainValidator(BaseModel):
    """Validateur pour les noms de domaine"""
    domain: str = Field(..., min_length=3, max_length=255)
    
    @field_validator('domain', mode='before')
    @classmethod
    def validate_domain(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Le domaine doit être une chaîne de caractères")
        
        value = value.strip().lower()
        
        # Enlever http(s):// si présent
        if value.startswith(('http://', 'https://')):
            parsed = urlparse(value)
            value = parsed.netloc or parsed.path
        
        # Enlever le slash final
        value = value.rstrip('/')
        
        # Validation regex pour nom de domaine
        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        )
        
        if not domain_regex.match(value):
            raise ValueError("Format de domaine invalide")
        
        # Vérifier qu'il n'y a pas d'adresse IP privée
        try:
            # Essayer de parser comme IP
            ip = ipaddress.ip_address(value.split(':')[0])
            if ip.is_private or ip.is_reserved or ip.is_loopback:
                raise ValueError("Adresses IP privées non autorisées")
        except ValueError:
            # Ce n'est pas une IP, c'est OK
            pass
        
        return value


class APIKeyValidator(BaseModel):
    """Validateur pour les clés API"""
    key: str = Field(..., min_length=10, max_length=200)
    
    @field_validator('key', mode='before')
    @classmethod
    def validate_api_key(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("La clé API doit être une chaîne de caractères")
        
        value = value.strip()
        
        # Vérifier qu'elle ne contient que des caractères autorisés
        if not re.match(r'^[a-zA-Z0-9\-_]+$', value):
            raise ValueError("La clé API contient des caractères non autorisés")
        
        return value


class EmailValidator(BaseModel):
    """Validateur pour les adresses email"""
    email: str = Field(..., min_length=5, max_length=254)
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("L'email doit être une chaîne de caractères")
        
        value = value.strip().lower()
        
        # Regex simple pour validation email
        email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        if not email_regex.match(value):
            raise ValueError("Format d'email invalide")
        
        return value


class QueryValidator(BaseModel):
    """Validateur pour les requêtes de recherche"""
    query: str = Field(..., min_length=1, max_length=500)
    
    @field_validator('query', mode='before')
    @classmethod
    def validate_query(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("La requête doit être une chaîne de caractères")
        
        value = value.strip()
        
        # Enlever les caractères de contrôle
        value = ''.join(char for char in value if ord(char) >= 32)
        
        # Limiter les caractères spéciaux consécutifs
        value = re.sub(r'[^\w\s]{3,}', '', value)
        
        if not value:
            raise ValueError("Requête vide après nettoyage")
        
        return value


class IntegerRangeValidator(BaseModel):
    """Validateur pour les entiers dans une plage"""
    value: int = Field(...)
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    
    @field_validator('value')
    @classmethod
    def validate_range(cls, v: int, info) -> int:
        data = info.data
        if data.get('min_value') is not None and v < data['min_value']:
            raise ValueError(f"Valeur doit être >= {data['min_value']}")
        if data.get('max_value') is not None and v > data['max_value']:
            raise ValueError(f"Valeur doit être <= {data['max_value']}")
        return v


def validate_file_path(path: str, must_exist: bool = False, 
                      allowed_extensions: Optional[List[str]] = None) -> Path:
    """
    Valide et sécurise un chemin de fichier
    
    Args:
        path: Chemin à valider
        must_exist: Si True, vérifie que le fichier existe
        allowed_extensions: Liste des extensions autorisées
    
    Returns:
        Path object validé
    
    Raises:
        ValueError: Si le chemin est invalide
    """
    validator = PathValidator(path=path)
    safe_path = Path(validator.path)
    
    if must_exist and not safe_path.exists():
        raise ValueError(f"Le fichier n'existe pas: {safe_path}")
    
    if allowed_extensions:
        if not any(safe_path.suffix.lower() == ext.lower() for ext in allowed_extensions):
            raise ValueError(f"Extension non autorisée. Autorisées: {allowed_extensions}")
    
    return safe_path


def validate_domain(domain: str) -> str:
    """
    Valide et nettoie un nom de domaine
    
    Args:
        domain: Domaine à valider
    
    Returns:
        Domaine validé et nettoyé
    
    Raises:
        ValueError: Si le domaine est invalide
    """
    validator = DomainValidator(domain=domain)
    return validator.domain


def validate_api_key(key: str) -> str:
    """
    Valide une clé API
    
    Args:
        key: Clé API à valider
    
    Returns:
        Clé API validée
    
    Raises:
        ValueError: Si la clé est invalide
    """
    validator = APIKeyValidator(key=key)
    return validator.key


def validate_email(email: str) -> str:
    """
    Valide une adresse email
    
    Args:
        email: Email à valider
    
    Returns:
        Email validé et normalisé
    
    Raises:
        ValueError: Si l'email est invalide
    """
    validator = EmailValidator(email=email)
    return validator.email


def validate_search_query(query: str) -> str:
    """
    Valide et nettoie une requête de recherche
    
    Args:
        query: Requête à valider
    
    Returns:
        Requête validée et nettoyée
    
    Raises:
        ValueError: Si la requête est invalide
    """
    validator = QueryValidator(query=query)
    return validator.query


def validate_integer_range(value: int, min_val: Optional[int] = None, 
                          max_val: Optional[int] = None) -> int:
    """
    Valide qu'un entier est dans une plage donnée
    
    Args:
        value: Valeur à valider
        min_val: Valeur minimale (incluse)
        max_val: Valeur maximale (incluse)
    
    Returns:
        Valeur validée
    
    Raises:
        ValueError: Si la valeur est hors plage
    """
    validator = IntegerRangeValidator(value=value, min_value=min_val, max_value=max_val)
    return validator.value


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour le rendre sûr
    
    Args:
        filename: Nom de fichier à nettoyer
    
    Returns:
        Nom de fichier sécurisé
    """
    # Enlever les caractères dangereux
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    
    # Limiter la longueur
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]
    
    filename = name + ext
    
    # Ne pas autoriser les noms réservés Windows
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    name_upper = name.upper()
    if name_upper in reserved_names:
        filename = f"_{filename}"
    
    return filename


def validate_json_safe(data: Any) -> bool:
    """
    Vérifie que les données peuvent être sérialisées en JSON en toute sécurité
    
    Args:
        data: Données à vérifier
    
    Returns:
        True si les données sont sûres pour JSON
    """
    import json
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError, RecursionError):
        return False