import os
from dotenv import load_dotenv

load_dotenv()


QDRANT_URL=os.getenv("qdrant_url")
QDRANT_KEY=os.getenv("qdrant_key")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
FASTAPI_BASE_URL=os.getenv("FASTAPI_BASE_URL")
MONGODB_URL=os.getenv("MONGODB_URL")
DATABASE_NAME=os.getenv("DATABASE_NAME")