from sqlalchemy import inspect, text
from app.database import engine

print("Adding OAuth columns to users table...")

with engine.begin() as conn:
    inspector = inspect(conn)
    if 'users' not in inspector.get_table_names():
        print("Users table doesn't exist - creating...")
        from app.database import Base
        Base.metadata.create_all(bind=engine)
    else:
        columns = {col['name'] for col in inspector.get_columns('users')}
        
        migrations = [
            ('full_name', "ALTER TABLE users ADD COLUMN full_name VARCHAR"),
            ('avatar_url', "ALTER TABLE users ADD COLUMN avatar_url VARCHAR"),
            ('auth_provider', "ALTER TABLE users ADD COLUMN auth_provider VARCHAR"),
            ('provider_subject', "ALTER TABLE users ADD COLUMN provider_subject VARCHAR"),
        ]
        
        for col_name, sql in migrations:
            if col_name not in columns:
                try:
                    conn.execute(text(sql))
                    print(f"✓ Added column: {col_name}")
                except Exception as e:
                    print(f"⚠ Column {col_name} may already exist: {e}")
            else:
                print(f"✓ Column {col_name} already exists")

print("Database schema updated!")
