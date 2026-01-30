"""
Logging middleware for FastAPI to log all requests and responses
"""
import time
import json
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_logger

logger = get_logger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Get request details
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        logger.info(
            f"REQUEST | {method} {path} | IP: {client_ip} | User-Agent: {user_agent[:100]}"
        )
        
        # Log request body for POST/PUT/PATCH (if available)
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON
                    try:
                        body_json = json.loads(body.decode())
                        # Mask sensitive fields
                        if isinstance(body_json, dict):
                            masked_body = self._mask_sensitive_data(body_json)
                            logger.debug(f"Request body: {json.dumps(masked_body, indent=2)}")
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        logger.debug(f"Request body (non-JSON): {len(body)} bytes")
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Get response details
            status_code = response.status_code
            response_size = response.headers.get("content-length", "unknown")
            
            # Log response
            log_level = logging.INFO if status_code < 400 else logging.WARNING if status_code < 500 else logging.ERROR
            logger.log(
                log_level,
                f"RESPONSE | {method} {path} | Status: {status_code} | Duration: {duration:.3f}s | Size: {response_size}"
            )
            
            # Log slow requests
            if duration > 1.0:
                logger.warning(
                    f"SLOW REQUEST | {method} {path} | Duration: {duration:.3f}s"
                )
            
            return response
            
        except Exception as e:
            # Log exception
            duration = time.time() - start_time
            logger.error(
                f"EXCEPTION | {method} {path} | Error: {str(e)} | Duration: {duration:.3f}s",
                exc_info=True
            )
            raise
    
    def _mask_sensitive_data(self, data: dict) -> dict:
        """Mask sensitive fields in request/response data"""
        sensitive_fields = [
            "password", "token", "access_token", "refresh_token",
            "api_key", "secret", "authorization", "auth"
        ]
        
        masked = data.copy()
        for key in masked.keys():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                masked[key] = "***MASKED***"
        
        return masked

