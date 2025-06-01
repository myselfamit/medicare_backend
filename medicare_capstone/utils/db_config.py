import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv # type: ignore
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_path = BASE_DIR / '.env.db'  # Use Path object

def db_connect():
    """
    Establishes a database connection and returns a session object.
    Uses environment variables for configuration.
    """
    try:
        load_dotenv(dotenv_path=str(env_path))  # Load environment variables
        # Load credentials from environment variables (or fallback to defaults)
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_port = os.getenv('DB_PORT')

        # Construct the database URL
        database_url = (
            f"mysql://{db_user}:{quote_plus(db_password)}@"
            f"{db_host}:{db_port}/{db_name}"
        )

        # Create engine with connection pooling and pre-ping to check connection
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=False
        )

        # Create session factory
        Session = sessionmaker(bind=engine)
        session = Session()

        # Test the connection
        session.execute("SELECT 1")  # Simple query to verify connection

        return session

    except Exception as e:
        print(f"Failed to connect to database: {str(e)}")
        raise  # Re-raise to let the caller handle it