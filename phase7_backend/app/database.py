from app.mongodb import MongoSession, get_mongo_db


def SessionLocal():
    return MongoSession()


def get_db():
    db = MongoSession()
    try:
        yield db
    finally:
        db.close()
