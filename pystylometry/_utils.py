"""Shared utility functions for pystylometry."""

from typing import List


def tokenize(text: str) -> List[str]:
    """
    Simple whitespace tokenization.

    Args:
        text: Input text to tokenize

    Returns:
        List of tokens
    """
    return text.split()


def split_sentences(text: str) -> List[str]:
    """
    Simple sentence splitting on common punctuation.

    Args:
        text: Input text to split

    Returns:
        List of sentences
    """
    # Simple implementation - can be improved with better sentence boundary detection
    import re
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def check_optional_dependency(module_name: str, extra_name: str) -> bool:
    """
    Check if an optional dependency is installed.

    Args:
        module_name: Name of the module to check
        extra_name: Name of the extra in pyproject.toml

    Returns:
        True if module is available

    Raises:
        ImportError: If module is not installed with instructions
    """
    try:
        __import__(module_name)
        return True
    except ImportError:
        raise ImportError(
            f"The '{module_name}' package is required for this functionality. "
            f"Install it with: pip install pystylometry[{extra_name}]"
        )
