"""
settings.py — urdhva_base configuration loader.

Reads from a .alg_env file in the current working directory using
pydantic-settings. Every service (api_manager, vendor_ingestion_api, …)
keeps its own .alg_env with the values appropriate for that service.

All settings have safe defaults so the service can at least start up and
report meaningful errors rather than crashing at import time.
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl


class Settings(BaseSettings):
    """
    Central settings object. Values are read from (in priority order):
      1. Environment variables
      2. .alg_env file in the current working directory
      3. Defaults defined here
    """

    model_config = SettingsConfigDict(
        env_file=".alg_env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",           # allow unknown keys in .alg_env without errors
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "NOVEX"

    # ── Database connections ──────────────────────────────────────────────────
    # Dict mapping connection-type label → list of DSN strings.
    # Example:
    #   db_urls = {
    #     "postgres_async": ["postgresql+asyncpg://host:5432/db?user=u&password=p"],
    #     "redis":          ["redis://localhost:6379"],
    #   }
    db_urls: Dict[str, List[Any]] = {
        "postgres_async": ["postgresql+asyncpg://localhost:5432/novex"],
        "redis": ["redis://localhost:6379"],
    }

    # ── Session / cookie ──────────────────────────────────────────────────────
    cookie_name: str = "ceg_session"
    session_httponly: bool = True
    # Must be False when running behind a plain-HTTP reverse proxy (nginx → uvicorn)
    session_secure: bool = False
    session_same_site: str = "lax"

    # ── Fernet key for cookie encryption ─────────────────────────────────────
    # Generate a fresh key:  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    fernet_key: str = "NjY5N2IwOWM5ZjE0MjMzN2M3YzA5Y2Y4ZDE4NTA2Mjk="

    # ── Payload encryption ────────────────────────────────────────────────────
    enable_encrypted_payload: bool = False

    # ── LDAP / Active Directory ───────────────────────────────────────────────
    ldap_host: str = "localhost"
    ldap_port: int = 389
    ldap_domain: str = "example.com"
    ldap_auth_enabled: bool = False

    # ── JWT (mobile / app auth) ───────────────────────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 1440  # 24 hours

    # ── Redis ─────────────────────────────────────────────────────────────────
    max_redis_connections: int = 20

    # ── Rate limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = 1000

    # ── Misc ──────────────────────────────────────────────────────────────────
    debug: bool = False
    log_level: str = "info"


# Module-level singleton — imported everywhere as `urdhva_base.settings`
settings = Settings()
