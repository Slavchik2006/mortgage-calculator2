"""Settings from environment variables (see .env.example)."""
import os

from .storage.base import ScenarioStore
from .storage.memory import MemoryScenarioStore


def build_store() -> ScenarioStore:
    if os.environ.get("STORAGE", "memory") == "supabase":
        from .storage.supabase import SupabaseScenarioStore

        return SupabaseScenarioStore(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    return MemoryScenarioStore()
