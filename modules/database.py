"""
Database Module
===============
Handles MongoDB connection and provides the db object used across all modules.
Falls back to an in-memory mock when MongoDB is not available (demo mode).
"""

import os
import streamlit as st
from datetime import datetime
from pymongo import MongoClient



# ─── Try real MongoDB first ───────────────────────────────────────────────────
try:
    MONGO_URI = st.secrets["mongodb+srv://servicebookadmin:ServiceBook%402026@women-safety-cluster.qtarrsa.mongodb.net/?appName=women-safety-cluster"]
except Exception:
    MONGO_URI = os.environ.get("mongodb+srv://servicebookadmin:ServiceBook%402026@women-safety-cluster.qtarrsa.mongodb.net/?appName=women-safety-cluster", "mongodb://localhost:27017/")

DB_NAME = "service_book_db"



class MockCollection:
    """In-memory collection that mimics basic pymongo Collection API."""

    def __init__(self, name):
        self.name = name
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {}
        if name not in st.session_state.mock_db:
            st.session_state.mock_db[name] = []

    @property
    def _data(self):
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {}
        if self.name not in st.session_state.mock_db:
            st.session_state.mock_db[self.name] = []
        return st.session_state.mock_db[self.name]

    # ── helpers ──────────────────────────────────────────────────────────────
    def _match(self, doc, query):
        """Simple equality / dot-notation matching."""
        for k, v in query.items():
            if k == "_id":
                continue
            # Support dot notation: "address.city"
            keys = k.split(".")
            val = doc
            try:
                for key in keys:
                    val = val[key]
            except (KeyError, TypeError):
                return False
            if isinstance(v, dict):
                # Handle $regex
                if "$regex" in v:
                    import re
                    flags = re.IGNORECASE if v.get("$options") == "i" else 0
                    if not re.search(v["$regex"], str(val), flags):
                        return False
                elif "$in" in v:
                    if val not in v["$in"]:
                        return False
                else:
                    if val != v:
                        return False
            else:
                if val != v:
                    return False
        return True

    def _project(self, doc, projection):
        if not projection:
            return doc
        include = {k for k, v in projection.items() if v == 1 and k != "_id"}
        exclude = {k for k, v in projection.items() if v == 0}
        if include:
            return {k: doc[k] for k in include if k in doc}
        result = dict(doc)
        for k in exclude:
            result.pop(k, None)
        return result

    # ── public API ────────────────────────────────────────────────────────────
    def insert_one(self, document):
        doc = dict(document)
        doc.setdefault("_id", str(datetime.utcnow().timestamp()).replace(".", ""))
        self._data.append(doc)
        class R:
            inserted_id = doc["_id"]
        return R()

    def find(self, query=None, projection=None):
        query = query or {}
        results = [self._project(d, projection) for d in self._data if self._match(d, query)]
        return results

    def find_one(self, query=None, projection=None):
        query = query or {}
        for d in self._data:
            if self._match(d, query):
                return self._project(d, projection)
        return None

    def update_one(self, query, update, upsert=False):
        for i, d in enumerate(self._data):
            if self._match(d, query):
                if "$set" in update:
                    self._data[i].update(update["$set"])
                if "$push" in update:
                    for field, value in update["$push"].items():
                        if field not in self._data[i]:
                            self._data[i][field] = []
                        self._data[i][field].append(value)
                if "$pull" in update:
                    for field, condition in update["$pull"].items():
                        if field in self._data[i]:
                            self._data[i][field] = [
                                item for item in self._data[i][field]
                                if not self._match(item, condition)
                            ]
                return
        if upsert:
            doc = dict(query)
            if "$set" in update:
                doc.update(update["$set"])
            self.insert_one(doc)

    def delete_one(self, query):
        for i, d in enumerate(self._data):
            if self._match(d, query):
                self._data.pop(i)
                return

    def count_documents(self, query=None):
        query = query or {}
        return sum(1 for d in self._data if self._match(d, query))

    def distinct(self, field, query=None):
        query = query or {}
        values = set()
        for d in self._data:
            if self._match(d, query) and field in d:
                values.add(d[field])
        return list(values)


class MockDB:
    """Mimics pymongo Database, returning MockCollection objects."""
    def __getattr__(self, name):
        return MockCollection(name)

    def __getitem__(self, name):
        return MockCollection(name)


# ── Connection logic ──────────────────────────────────────────────────────────
_real_db = None

def _try_connect():
    global _real_db
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")          # Fast connection test
        _real_db = client[DB_NAME]

        # Ensure indexes
        _real_db.employees.create_index("employee_id", unique=True)
        _real_db.audit_logs.create_index("timestamp")
        return _real_db
    except Exception:
        return None


def get_db():
    """Return real MongoDB db or fall back to in-memory mock."""
    real = _try_connect()
    if real is not None:
        return real
    return MockDB()


db = get_db()


def is_mock():
    return isinstance(db, MockDB)