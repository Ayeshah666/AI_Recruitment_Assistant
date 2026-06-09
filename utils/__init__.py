"""
Utils package for AI Recruitment Assistant
"""

from . import auth
from . import database
from . import style
from . import ollama_client

# Export commonly used functions
from .ollama_client import (
    analyze_resume,
    generate_cover_letter,
    generate_interview_questions,
    check_ollama,
    stream_cover_letter
)

from .auth import authenticate_user, logout, hash_password, verify_password
from .database import db_client, db
from .style import (
    inject_custom_css,
    stat_card,
    fancy_divider,
    glass_card,
    question_card,
    hero_section,
    feature_card,
    status_badge,
    page_header,
    infobox,
    ollama_pill
)

__all__ = [
    # Auth
    'authenticate_user', 'logout', 'hash_password', 'verify_password',
    # Database
    'db_client', 'db',
    # Style
    'inject_custom_css', 'stat_card', 'fancy_divider', 'glass_card',
    'question_card', 'hero_section', 'feature_card', 'status_badge',
    'page_header', 'infobox', 'ollama_pill',
    # Ollama
    'analyze_resume', 'generate_cover_letter', 'generate_interview_questions',
    'check_ollama', 'stream_cover_letter'
]
