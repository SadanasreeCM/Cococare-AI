from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

    # Check and migrate detections table for block_id and farmer_notes columns if using SQLite
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE detections ADD COLUMN block_id INTEGER REFERENCES farm_blocks(id)"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE detections ADD COLUMN farmer_notes TEXT"))
            conn.commit()
        except Exception:
            pass

    # Ensure default demo user exists (id=1) so farm setup works for unauthenticated/demo sessions

    db = SessionLocal()
    try:
        from backend.models import User
        default_user = db.query(User).filter(User.id == 1).first()
        if not default_user:
            default_user = User(
                id=1,
                username="default_farmer",
                password_hash="8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
                preferred_language="en"
            )
            db.add(default_user)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

