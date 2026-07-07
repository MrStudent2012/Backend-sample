# Database configuration
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
