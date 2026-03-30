from sqlalchemy import inspect, text
from app.database import engine

try:
    inspector = inspect(engine)
    if 'users' in inspector.get_table_names():
        columns = inspector.get_columns('users')
        print("Users table columns:")
        for col in columns:
            print(f"  {col['name']}: {col['type']}")
    else:
        print("Users table does not exist - creating...")
        from app.database import Base
        Base.metadata.create_all(bind=engine)
        print("Schema created")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
