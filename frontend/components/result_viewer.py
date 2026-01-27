"""Result viewer component."""
import streamlit as st
from typing import Optional


def render(document: dict, parse_result: Optional[dict] = None):
    """Render document viewer with original and parsed results.
    
    Args:
        document: Document info dict
        parse_result: Parse result dict (optional)
    """
    raise NotImplementedError
