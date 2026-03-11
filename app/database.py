from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "adaptive_diagnostic")

_client = None
_use_mock = False

_PLACEHOLDER_MARKERS = ["<username>", "<password>", "sk-...", ""]


def _is_placeholder(uri: str) -> bool:
    return not uri or any(m in uri for m in _PLACEHOLDER_MARKERS)


def get_db():
    """
    Return the MongoDB database instance.
    Falls back to an in-memory mongomock database when MONGO_URI is
    not configured (useful for demos and local development without Atlas).
    """
    global _client, _use_mock
    if _client is None:
        if _is_placeholder(MONGO_URI):
            try:
                import mongomock
                _client = mongomock.MongoClient()
                _use_mock = True
                print("⚠️  MONGO_URI not set — using in-memory mock database (demo mode).")
            except ImportError:
                raise RuntimeError(
                    "mongomock is not installed and MONGO_URI is not configured. "
                    "Run: pip install mongomock  OR set a real MONGO_URI in .env"
                )
        else:
            try:
                _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                _client.admin.command("ping")
                print("✅ Connected to MongoDB Atlas successfully.")
            except ConnectionFailure as e:
                raise RuntimeError(f"❌ Could not connect to MongoDB: {e}")
    return _client[DATABASE_NAME]


def get_questions_collection():
    return get_db()["questions"]


def get_sessions_collection():
    return get_db()["sessions"]

