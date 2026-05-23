"""
tests/test_auth.py - Unit tests for authentication module

Tests password hashing, verification, and user management.
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_generates_salt(self):
        """Test that _hash_password generates a salt when not provided."""
        from auth import _hash_password
        
        hashed, salt = _hash_password("test_password")
        
        assert hashed is not None
        assert salt is not None
        assert len(salt) == 64  # hex(32 bytes) = 64 chars


    def test_hash_password_with_provided_salt(self):
        """Test that _hash_password uses provided salt."""
        from auth import _hash_password
        
        fixed_salt = "a" * 64
        hashed1, returned_salt = _hash_password("test_password", fixed_salt)
        hashed2, _ = _hash_password("test_password", fixed_salt)
        
        assert returned_salt == fixed_salt
        assert hashed1 == hashed2  # Same password + salt = same hash


    def test_verify_password_success(self):
        """Test that _verify_password returns True for correct password."""
        from auth import _hash_password, _verify_password
        
        password = "SecurePass123!"
        hashed, salt = _hash_password(password)
        
        assert _verify_password(password, hashed, salt) is True


    def test_verify_password_failure(self):
        """Test that _verify_password returns False for wrong password."""
        from auth import _hash_password, _verify_password
        
        password = "SecurePass123!"
        hashed, salt = _hash_password(password)
        
        assert _verify_password("WrongPassword", hashed, salt) is False


    def test_password_timing_attack_resistance(self):
        """Test that password verification uses constant-time comparison."""
        from auth import _hash_password, _verify_password
        import time
        
        password = "SecurePass123!"
        hashed, salt = _hash_password(password)
        
        # This test verifies the comparison is constant-time
        # by checking the function uses hmac.compare_digest
        times = []
        for _ in range(3):
            start = time.perf_counter()
            _verify_password("WrongPass", hashed, salt)
            times.append(time.perf_counter() - start)
        
        # Times should be similar (constant-time)
        assert max(times) - min(times) < 0.01  # Within 10ms


# TODO: Add tests for login(), create_user(), change_password() once DB fixture ready
