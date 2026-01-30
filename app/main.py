from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.api_v1.api import api_router
from .core.config import settings
from .core.logging_config import setup_logging, get_logger
from .middleware.logging_middleware import LoggingMiddleware

# Initialize logging
setup_logging(log_level=getattr(settings, 'LOG_LEVEL', 'INFO'))
app_logger = get_logger("app")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add logging middleware (before CORS to log all requests)
app.add_middleware(LoggingMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Log application startup"""
    app_logger.info("=" * 80)
    app_logger.info(f"Starting {settings.PROJECT_NAME} API")
    app_logger.info(f"API Version: {settings.API_V1_STR}")
    app_logger.info("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    app_logger.info("=" * 80)
    app_logger.info(f"Shutting down {settings.PROJECT_NAME} API")
    app_logger.info("=" * 80)

@app.get("/")
def root():
    app_logger.debug("Root endpoint accessed")
    return {"message": "Welcome to CMO AI API"}

@app.get("/health")
def health_check():
    app_logger.debug("Health check endpoint accessed")
    return {"status": "healthy"}
