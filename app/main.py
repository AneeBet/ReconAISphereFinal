from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.database import engine

# IMPORTANT:
# Import all models so SQLAlchemy registers them
import app.models

from app.middleware.logging import (
    RequestLoggingMiddleware
)

from app.exceptions.handlers import (
    register_exception_handlers
)

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.files import router as files_router
from app.api.transactions import router as transactions_router
from app.api.reconciliation import router as reconciliation_router
from app.api.exceptions import router as exceptions_router
from app.api.cases import router as cases_router
from app.api.ai import router as ai_router
from app.api.reports import router as reports_router
from app.api.audit import router as audit_router
from app.api.settings import router as settings_router
from app.api.seed_users import (
    router as seed_users_router
)


@asynccontextmanager
async def lifespan(
    app: FastAPI
):
    #
    # Create database tables if they do not exist.
    # Safe to execute on every startup.
    #
    Base.metadata.create_all(
        bind=engine
    )

    yield


app = FastAPI(

    title="ReconAI API",

    version="1.0.0",

    lifespan=lifespan

)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)


app.add_middleware(
    RequestLoggingMiddleware
)


register_exception_handlers(
    app
)


#
# API Routers
#

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(files_router)
app.include_router(transactions_router)
app.include_router(reconciliation_router)
app.include_router(exceptions_router)
app.include_router(cases_router)
app.include_router(ai_router)
app.include_router(reports_router)
app.include_router(audit_router)
app.include_router(settings_router)
app.include_router(seed_users_router)


@app.get("/health")
def health():

    return {

        "status": "healthy",

        "service": "ReconAI",

        "version": "1.0.0"

    }