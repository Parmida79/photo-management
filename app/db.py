from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, configure_mappers
from urllib.parse import urlparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sqlalchemy_searchable import make_searchable

from app.config import settings

# Parse database URL to extract components
def parse_database_url(url: str):
    """Parse database URL into components."""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/'),
    }


def create_database_if_not_exists():
    """Create database if it doesn't exist."""
    db_config = parse_database_url(settings.database_url)
    database_name = db_config['database']
    
    # Connect to postgres database to create the target database
    postgres_url = settings.database_url.rsplit('/', 1)[0] + '/postgres'
    postgres_config = parse_database_url(postgres_url)
    
    try:
        conn = psycopg2.connect(
            host=postgres_config['host'],
            port=postgres_config['port'],
            user=postgres_config['user'],
            password=postgres_config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (database_name,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create the database
            cursor.execute(f'CREATE DATABASE "{database_name}"')
            print(f"Database '{database_name}' created successfully")
        else:
            print(f"Database '{database_name}' already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise


engine = create_engine(
    url=settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=True,
    pool_use_lifo=True,
    connect_args={"options": "-c timezone=utc"}
)


Base = declarative_base()
make_searchable(Base.metadata)
configure_mappers()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables(engine):
    """Create database if it doesn't exist, then create all tables."""
    # First, ensure the database exists
    create_database_if_not_exists()
    
    # Then create the tables
    configure_mappers()
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# for basedata for the time being
def drop_and_create_db(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

