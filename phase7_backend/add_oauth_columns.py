from sqlalchemy import inspect, text, Column, String
from app.database import engine

with engine.begin() as conn:
    inspector = inspect(conn)
    columns = {col['name'] for col in inspector.get_columns('users')}
    
    if 'full_name' not in columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))
        print("Added: full_name")
    
    if 'avatar_url' not in columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))
        print("Added: avatar_url")
    
    if 'auth_provider' not in columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR"))
        print("Added: auth_provider")
    
    if 'provider_subject' not in columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN provider_subject VARCHAR"))
        print("Added: provider_subject")

print("Database schema updated successfully!")
