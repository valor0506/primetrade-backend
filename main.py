from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.db.base import Base
from app.db.session import engine

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PrimeTrade API",
    description="""
## PrimeTrade Backend API

A secure, scalable REST API for trade management with JWT authentication and role-based access control.

### Authentication
- Register a new account at `/api/v1/auth/register`
- Login at `/api/v1/auth/login` to receive a JWT token
- Include the token as `Bearer <token>` in the `Authorization` header

### Roles
- **user** — can manage their own trades
- **admin** — can view all users and all trades, update roles
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow frontend dev server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )


app.include_router(api_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "PrimeTrade API", "version": "1.0.0"}
