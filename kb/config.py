"""All settings come from the environment, so swapping the LLM or the IdP is a config change."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    db_path: Path = Path(os.getenv("KB_DB", ROOT / "kb.db"))
    embed_model: str = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    llm_model: str = os.getenv("LLM_MODEL", "qwen2.5:7b")
    llm_api_key: str = os.getenv("LLM_API_KEY", "ollama")
    oidc_issuer: str = os.getenv("OIDC_ISSUER", "http://localhost:8080/realms/vardhan")
    oidc_client_id: str = os.getenv("OIDC_CLIENT_ID", "kb-app")
    oidc_client_secret: str = os.getenv("OIDC_CLIENT_SECRET", "")
    app_url: str = os.getenv("APP_URL", "http://localhost:8000")
    company_domain: str = os.getenv("COMPANY_DOMAIN", "vardhanpumps.in")
    audit_group: str = os.getenv("AUDIT_GROUP", "security-admins")


settings = Settings()
