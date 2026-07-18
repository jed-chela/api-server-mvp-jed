import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import os

from app.database.session import engine
from app.database.base import Base

from app.api.v1.router import api_router
from app.core.logging import logger


# ----------------------------------
# Create tables & directories
# ----------------------------------

Base.metadata.create_all(bind=engine)
os.makedirs(os.path.join("static", "photos"), exist_ok=True)


# ----------------------------------
# FastAPI App
# ----------------------------------

app = FastAPI(title="Afamilia API")

# Serve static files (Firebase uploads placeholder)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Register routers

app.include_router(api_router)


# ----------------------------------
# Startup event
# ----------------------------------

@app.on_event("startup")
def startup():

    logger.info("🔄 Checking database connection...")

    try:
        with engine.connect() as connection:

            result = connection.execute(text("SELECT 1"))

            row = result.scalar()

            logger.info("✅ Database connection successful")
            logger.info(f"📦 Database test query result: {row}")

    except SQLAlchemyError as e:

        logger.error("❌ Database connection failed")
        logger.error(str(e))