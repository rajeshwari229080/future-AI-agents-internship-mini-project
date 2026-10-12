"""
Launcher script for the Student Record Management System.
Executes the FastAPI application using Uvicorn.
"""

import sys
import uvicorn
from app.config import settings

def main():
    print("=" * 65)
    print(f" Starting {settings.APP_NAME}")
    print(f" Environment : {settings.APP_ENV}")
    print(f" Database    : {settings.DATABASE_URL}")
    print(f" Dashboard   : http://{settings.HOST}:{settings.PORT}")
    print(f" API Docs    : http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 65)

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

if __name__ == "__main__":
    main()
