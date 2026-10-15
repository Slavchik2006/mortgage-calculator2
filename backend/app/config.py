"""Settings from environment variables (see .env.example)."""
import os

from .storage.base import ScenarioStore
from .storage.memory import MemoryScenarioStore


def build_store() -> ScenarioStore:
    if os.environ.get("STORAGE", "memory") == "supabase":
        from .storage.supabase import SupabaseScenarioStore

        store = SupabaseScenarioStore(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
        store.verify_parameters()  # refuse to start if the database catalog drifted from the code
        return store
    return MemoryScenarioStore()
