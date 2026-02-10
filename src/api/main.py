import os
import secrets
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .routes import license as license_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="InnerSource License Generator",
    description="Generate customized InnerSource software licenses",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# SESSION_HTTPS_ONLY: set to 'true' in production (HTTPS); defaults to false for local HTTP dev
_https_only = os.getenv('SESSION_HTTPS_ONLY', 'false').lower() == 'true'
_secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Add session middleware for temporary state (like download sessions)
app.add_middleware(
    SessionMiddleware,
    secret_key=_secret_key,
    session_cookie="license_session",
    max_age=600,  # 10 minutes
    same_site="lax",
    https_only=_https_only,
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include routers
app.include_router(license_router.router)


@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    debug = True if os.getenv('DEBUG_FASTAPI') else False
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=debug,
        log_level="info"
    )
