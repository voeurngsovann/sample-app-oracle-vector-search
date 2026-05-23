"""
validation.py - Input validation utilities

Centralized validation functions for user inputs, files, and parameters.
All validation errors raise specific exceptions with clear messages.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import constants


class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
#  File Validation
# ─────────────────────────────────────────────────────────────────────────────
def validate_file_upload(filename: str, file_data: bytes) -> tuple[bool, str]:
    """
    Validate uploaded file for size, type, and content.
    
    Args:
        filename: The filename (with extension)
        file_data: The raw file bytes
        
    Returns:
        (is_valid, error_message) tuple
    """
    # Validate filename exists
    if not filename:
        return False, "Filename cannot be empty"
    
    # Validate file size
    if len(file_data) > constants.VALIDATION_FILE_MAX_BYTES:
        return False, f"File exceeds maximum size of {constants.VALIDATION_FILE_MAX_BYTES / (1024*1024):.0f} MB"
    
    if len(file_data) == 0:
        return False, "File is empty"
    
    # Validate file extension
    ext = "." + filename.rsplit(".", 1)[-1].lower()
    if ext not in constants.CHUNKER_SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file type. Supported: {', '.join(constants.CHUNKER_SUPPORTED_EXTENSIONS)}"
    
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
#  Query Validation
# ─────────────────────────────────────────────────────────────────────────────
def validate_search_query(query: str) -> tuple[bool, str]:
    """
    Validate search query input.
    
    Args:
        query: The search query string
        
    Returns:
        (is_valid, error_message) tuple
    """
    if not query:
        return False, "Query cannot be empty"
    
    query_stripped = query.strip()
    
    if len(query_stripped) < constants.VALIDATION_QUERY_MIN_LENGTH:
        return False, f"Query must be at least {constants.VALIDATION_QUERY_MIN_LENGTH} characters"
    
    if len(query_stripped) > constants.VALIDATION_QUERY_MAX_LENGTH:
        return False, f"Query cannot exceed {constants.VALIDATION_QUERY_MAX_LENGTH} characters"
    
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
#  Database Parameter Validation
# ─────────────────────────────────────────────────────────────────────────────
def validate_top_k(top_k: int | None) -> tuple[bool, str]:
    """Validate top_k parameter for vector search."""
    if top_k is None:
        return True, ""  # None means use default
    
    if not isinstance(top_k, int):
        return False, f"top_k must be integer, got {type(top_k).__name__}"
    
    if top_k <= 0:
        return False, f"top_k must be positive, got {top_k}"
    
    if top_k > 1000:
        return False, f"top_k exceeds maximum of 1000, got {top_k}"
    
    return True, ""


def validate_distance_metric(distance: str | None) -> tuple[bool, str]:
    """Validate distance metric for vector search."""
    valid_metrics = ("COSINE", "EUCLIDEAN", "MANHATTAN", "HAMMING")
    
    if distance is None:
        return True, ""  # None means use default
    
    distance_upper = distance.upper()
    if distance_upper not in valid_metrics:
        return False, f"Distance metric must be one of {valid_metrics}, got {distance}"
    
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
#  Authentication Validation
# ─────────────────────────────────────────────────────────────────────────────
def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format."""
    if not username:
        return False, "Username cannot be empty"
    
    username_stripped = username.strip()
    
    if len(username_stripped) < constants.VALIDATION_USERNAME_MIN_LENGTH:
        return False, f"Username must be at least {constants.VALIDATION_USERNAME_MIN_LENGTH} characters"
    
    # Allow alphanumeric, underscore, hyphen
    if not all(c.isalnum() or c in ('_', '-') for c in username_stripped):
        return False, "Username can only contain letters, numbers, underscore, and hyphen"
    
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < constants.VALIDATION_PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {constants.VALIDATION_PASSWORD_MIN_LENGTH} characters"
    
    return True, ""
