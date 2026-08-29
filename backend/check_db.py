import sys
import sqlalchemy
from app.db.database import engine

def main():
    if not engine:
        print("Engine not initialized")
        sys.exit(1)
        
    try:
        if engine.name == 'sqlite':
            print("Running on SQLite (RLS does not apply)")
            sys.exit(0)
            
        with engine.connect() as conn:
            # Postgres specific queries
            current_user = conn.execute(sqlalchemy.text("SELECT current_user;")).scalar()
            session_user = conn.execute(sqlalchemy.text("SELECT session_user;")).scalar()
            
            # Check bypass rls
            bypass_rls = conn.execute(sqlalchemy.text(
                f"SELECT rolbypassrls FROM pg_roles WHERE rolname = '{current_user}';"
            )).scalar()
            
            print(f"Role: {current_user}")
            print(f"Session: {session_user}")
            print(f"Bypass RLS: {bypass_rls}")
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    main()
