"""
database.py
-----------
MongoDB client with transparent in-memory fallback.
The module exposes a single `db` instance — import that, never
instantiate MongoDBClient elsewhere.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
from pymongo import DESCENDING, MongoClient
from pymongo.errors import PyMongoError


# ─────────────────────────────────────────────
# In-memory store (used when Mongo is absent)
# ─────────────────────────────────────────────

class _InMemoryStore:
    def __init__(self) -> None:
        self._users: List[Dict] = []
        self._applications: List[Dict] = []
        self._analyses: List[Dict] = []
        self._interview_notes: List[Dict] = []
        self._interview_reminders: List[Dict] = []
        self._counter = 0

    def _new_id(self) -> str:
        self._counter += 1
        return f"mem_{self._counter}"


# ─────────────────────────────────────────────
# Main client
# ─────────────────────────────────────────────

class MongoDBClient:
    DB_NAME = "job_assistant"

    def __init__(self) -> None:
        self._mongo: Optional[MongoClient] = None
        self._mem = _InMemoryStore()
        self.connected = False
        self._connect()

    # ── Connection ───────────────────────────

    def _get_uri(self) -> str:
        try:
            uri = st.secrets.get("MONGODB_URI")
            if uri:
                return uri
        except Exception:
            pass
        return os.getenv("MONGODB_URI", "mongodb://localhost:27017")

    def _connect(self) -> None:
        try:
            client = MongoClient(self._get_uri(), serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            self._mongo = client
            self.connected = True
        except Exception as exc:
            print(f"[DB] MongoDB unavailable ({exc}). Using in-memory store.")
            self._mongo = None
            self.connected = False

    @property
    def _db(self):
        if not self.connected:
            self._connect()
        if self._mongo is not None:
            return self._mongo[self.DB_NAME]
        return None

    # ── Users ────────────────────────────────

    def create_user(
        self, username: str, email: str, name: str, hashed_password: str
    ) -> bool:
        """Returns True on success, False if username already taken."""
        try:
            db = self._db
            if db is not None:
                if db.users.find_one({"username": username}):
                    return False
                db.users.insert_one(
                    {
                        "username": username,
                        "email": email,
                        "name": name,
                        "password": hashed_password,
                        "created_at": datetime.utcnow(),
                    }
                )
                return True
            # In-memory fallback
            if any(u["username"] == username for u in self._mem._users):
                return False
            self._mem._users.append(
                {
                    "_id": self._mem._new_id(),
                    "username": username,
                    "email": email,
                    "name": name,
                    "password": hashed_password,
                }
            )
            return True
        except PyMongoError as exc:
            print(f"[DB] create_user: {exc}")
            return False

    def get_user(self, username: str) -> Optional[Dict]:
        """Return user document or None."""
        try:
            db = self._db
            if db is not None:
                return db.users.find_one({"username": username})
            return next(
                (u for u in self._mem._users if u["username"] == username), None
            )
        except Exception:
            return None

    # ── Applications ─────────────────────────

    def save_application(self, user_id: str, data: Dict) -> Optional[str]:
        """Alias for add_application - saves an application"""
        return self.add_application(user_id, data)

    def add_application(self, user_id: str, data: Dict) -> Optional[str]:
        data = {
            **data,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
        }
        try:
            db = self._db
            if db is not None:
                result = db.applications.insert_one(data)
                return str(result.inserted_id)
            doc_id = self._mem._new_id()
            data["_id"] = doc_id
            self._mem._applications.append(data)
            return doc_id
        except Exception as exc:
            print(f"[DB] add_application: {exc}")
            return None

    def get_applications(
        self, user_id: str, status: Optional[str] = None
    ) -> List[Dict]:
        try:
            db = self._db
            if db is not None:
                query: Dict[str, Any] = {"user_id": user_id}
                if status:
                    query["status"] = status
                return list(
                    db.applications.find(query).sort("applied_date", DESCENDING)
                )
            apps = [a for a in self._mem._applications if a.get("user_id") == user_id]
            if status:
                apps = [a for a in apps if a.get("status") == status]
            return sorted(
                apps, key=lambda x: x.get("applied_date", datetime.min), reverse=True
            )
        except Exception as exc:
            print(f"[DB] get_applications: {exc}")
            return []

    def update_application(self, app_id: Any, data: Dict) -> bool:
        try:
            data["last_updated"] = datetime.utcnow()
            db = self._db
            if db is not None:
                from bson import ObjectId

                oid = ObjectId(app_id) if isinstance(app_id, str) else app_id
                db.applications.update_one({"_id": oid}, {"$set": data})
                return True
            for i, a in enumerate(self._mem._applications):
                if a.get("_id") == app_id:
                    self._mem._applications[i].update(data)
                    return True
            return False
        except Exception as exc:
            print(f"[DB] update_application: {exc}")
            return False

    def delete_application(self, app_id: Any) -> bool:
        try:
            db = self._db
            if db is not None:
                from bson import ObjectId

                oid = ObjectId(app_id) if isinstance(app_id, str) else app_id
                db.applications.delete_one({"_id": oid})
                return True
            before = len(self._mem._applications)
            self._mem._applications = [
                a for a in self._mem._applications if a.get("_id") != app_id
            ]
            return len(self._mem._applications) < before
        except Exception as exc:
            print(f"[DB] delete_application: {exc}")
            return False

    def get_stats(self, user_id: str) -> Dict[str, int]:
        apps = self.get_applications(user_id)
        return {
            "total": len(apps),
            "applied": sum(1 for a in apps if a.get("status") == "Applied"),
            "interview": sum(1 for a in apps if a.get("status") == "Interview"),
            "offer": sum(1 for a in apps if a.get("status") == "Offer"),
            "rejected": sum(1 for a in apps if a.get("status") == "Rejected"),
        }

    # ── Resume analyses ──────────────────────

    def save_analysis(self, user_id: str, data: Dict) -> Optional[str]:
        data = {**data, "user_id": user_id, "saved_at": datetime.utcnow()}
        try:
            db = self._db
            if db is not None:
                result = db.analyses.insert_one(data)
                return str(result.inserted_id)
            doc_id = self._mem._new_id()
            data["_id"] = doc_id
            self._mem._analyses.append(data)
            return doc_id
        except Exception as exc:
            print(f"[DB] save_analysis: {exc}")
            return None

    # ── Interview notes ──────────────────────

    def save_interview_prep(self, user_id: str, company: str, position: str, notes: str) -> Optional[str]:
        """Save interview preparation notes"""
        data = {
            "user_id": user_id,
            "company": company,
            "position": position,
            "notes": notes,
            "saved_at": datetime.utcnow(),
        }
        try:
            db = self._db
            if db is not None:
                result = db.interview_notes.insert_one(data)
                return str(result.inserted_id)
            doc_id = self._mem._new_id()
            data["_id"] = doc_id
            self._mem._interview_notes.append(data)
            return doc_id
        except Exception as exc:
            print(f"[DB] save_interview_prep: {exc}")
            return None

    def save_interview_notes(
        self, user_id: str, company: str, position: str, notes: str
    ) -> Optional[str]:
        return self.save_interview_prep(user_id, company, position, notes)
    
    # ── Interview reminders ──────────────────
    
    def save_interview_reminder(self, user_id: str, company: str, position: str, 
                                 interview_date: str, interview_time: str) -> Optional[str]:
        """Save an interview reminder"""
        data = {
            "user_id": user_id,
            "company": company,
            "position": position,
            "interview_date": interview_date,
            "interview_time": interview_time,
            "created_at": datetime.utcnow(),
        }
        try:
            db = self._db
            if db is not None:
                result = db.interview_reminders.insert_one(data)
                return str(result.inserted_id)
            doc_id = self._mem._new_id()
            data["_id"] = doc_id
            self._mem._interview_reminders.append(data)
            return doc_id
        except Exception as exc:
            print(f"[DB] save_interview_reminder: {exc}")
            return None
    
    def get_interview_reminders(self, user_id: str) -> List[Dict]:
        """Get all interview reminders for a user"""
        try:
            db = self._db
            if db is not None:
                return list(db.interview_reminders.find({"user_id": user_id}))
            return [r for r in self._mem._interview_reminders if r.get("user_id") == user_id]
        except Exception as exc:
            print(f"[DB] get_interview_reminders: {exc}")
            return []
    
    def delete_interview_reminder(self, reminder_id: Any) -> bool:
        """Delete an interview reminder"""
        try:
            db = self._db
            if db is not None:
                from bson import ObjectId
                oid = ObjectId(reminder_id) if isinstance(reminder_id, str) else reminder_id
                db.interview_reminders.delete_one({"_id": oid})
                return True
            before = len(self._mem._interview_reminders)
            self._mem._interview_reminders = [
                r for r in self._mem._interview_reminders if r.get("_id") != reminder_id
            ]
            return len(self._mem._interview_reminders) < before
        except Exception as exc:
            print(f"[DB] delete_interview_reminder: {exc}")
            return False


# Module-level singleton
db = MongoDBClient()
db_client = db  # Alias for compatibility