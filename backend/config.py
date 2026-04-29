import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_config = None


class Config:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.browser_headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

        raw_dirs = os.getenv("ALLOWED_DIRECTORIES", "./workspace")
        self.allowed_directories = [
            Path(d.strip()).expanduser().resolve() for d in raw_dirs.split(",") if d.strip()
        ]

        self.credentials = {}
        cred_path = Path("credentials.json")
        if cred_path.exists():
            with open(cred_path) as f:
                self.credentials = json.load(f)

    def validate_path(self, path: str) -> Path:
        resolved = Path(path).expanduser().resolve()
        for allowed in self.allowed_directories:
            if resolved == allowed or allowed in resolved.parents:
                return resolved
        raise PermissionError(
            f"Path '{path}' is not within allowed directories: "
            f"{[str(d) for d in self.allowed_directories]}"
        )

    def get_site_credentials(self, site_key: str) -> dict:
        sites = self.credentials.get("sites", {})
        if site_key not in sites:
            raise KeyError(f"No credentials found for site '{site_key}'. Available: {list(sites.keys())}")
        return sites[site_key]


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
