import os
from datetime import datetime
import pymongo
from pymongo import MongoClient
from app.config import MONGODB_URL

_client = None
_mongo_db = None


import certifi


def get_mongo_db():
    global _client, _mongo_db
    if _mongo_db is None:
        try:
            _client = MongoClient(MONGODB_URL, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
            _mongo_db = _client.get_database()
            _client.admin.command("ping")
        except Exception:
            _client = MongoClient(MONGODB_URL, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=10000)
            _mongo_db = _client.get_database()
    return _mongo_db


class Field:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return {self.name: other}

    def __ne__(self, other):
        return {self.name: {"$ne": other}}

    def desc(self):
        return (self.name, -1)

    def asc(self):
        return (self.name, 1)


class MongoQuery:
    def __init__(self, collection, model_cls, db_session):
        self.collection = collection
        self.model_cls = model_cls
        self.db_session = db_session
        self.filter_spec = {}
        self.sort_spec = None

    def filter(self, *criterions):
        for c in criterions:
            if isinstance(c, dict):
                self.filter_spec.update(c)
        return self

    def order_by(self, *criterions):
        sort_list = []
        for c in criterions:
            if isinstance(c, tuple) and len(c) == 2:
                sort_list.append(c)
            elif isinstance(c, Field):
                sort_list.append((c.name, 1))
        if sort_list:
            self.sort_spec = sort_list
        return self

    def first(self):
        if self.sort_spec:
            cursor = self.collection.find(self.filter_spec).sort(self.sort_spec).limit(1)
            docs = list(cursor)
            doc = docs[0] if docs else None
        else:
            doc = self.collection.find_one(self.filter_spec)

        if not doc:
            return None
        return self.model_cls.from_doc(doc, self.db_session)

    def all(self):
        cursor = self.collection.find(self.filter_spec)
        if self.sort_spec:
            cursor = cursor.sort(self.sort_spec)
        return [self.model_cls.from_doc(doc, self.db_session) for doc in cursor]

    def count(self):
        return self.collection.count_documents(self.filter_spec)


class MongoSession:
    def __init__(self):
        self.mongo_db = get_mongo_db()
        self.pending_add = []
        self.pending_delete = []

    def query(self, model_cls):
        collection_name = getattr(model_cls, "__collection_name__", "default")
        return MongoQuery(self.mongo_db[collection_name], model_cls, self)

    def add(self, item):
        if item not in self.pending_add:
            self.pending_add.append(item)

    def delete(self, item):
        if item not in self.pending_delete:
            self.pending_delete.append(item)

    def flush(self):
        self.commit()

    def commit(self):
        for item in self.pending_add:
            item.save(self.mongo_db)
        self.pending_add.clear()

        for item in self.pending_delete:
            item.delete_from_db(self.mongo_db)
        self.pending_delete.clear()

    def refresh(self, item):
        item.reload(self.mongo_db)

    def close(self):
        pass
