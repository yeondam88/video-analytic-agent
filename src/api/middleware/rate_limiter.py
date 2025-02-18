from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from typing import Dict, Tuple
import asyncio
from loguru import logger

class RateLimiter:
    """Rate limiting middleware using token bucket algorithm."""
    
    def __init__(self, tokens_per_second: float = 10.0, bucket_size: int = 100):
        self.tokens_per_second = tokens_per_second
        self.bucket_size = bucket_size
        self.buckets: Dict[str, Tuple[float, float]] = {}  # {ip: (tokens, last_update)}
        self._cleanup_task = None
    
    async def cleanup_buckets(self):
        """Periodically cleanup old bucket entries."""
        while True:
            try:
                current_time = time.time()
                expired_ips = [
                    ip for ip, (_, last_update) in self.buckets.items()
                    if current_time - last_update > 3600  # Remove after 1 hour of inactivity
                ]
                for ip in expired_ips:
                    del self.buckets[ip]
                await asyncio.sleep(3600)  # Run cleanup every hour
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
                await asyncio.sleep(3600)
    
    def start_cleanup(self):
        """Start the cleanup task."""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self.cleanup_buckets())
    
    def stop_cleanup(self):
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None
    
    def _get_tokens(self, ip: str) -> float:
        """Get current token count for an IP."""
        current_time = time.time()
        if ip not in self.buckets:
            self.buckets[ip] = (self.bucket_size, current_time)
            return self.bucket_size
            
        tokens, last_update = self.buckets[ip]
        time_passed = current_time - last_update
        new_tokens = min(
            self.bucket_size,
            tokens + time_passed * self.tokens_per_second
        )
        self.buckets[ip] = (new_tokens, current_time)
        return new_tokens
    
    def _consume_token(self, ip: str) -> bool:
        """Attempt to consume a token for an IP."""
        tokens = self._get_tokens(ip)
        if tokens >= 1:
            self.buckets[ip] = (tokens - 1, self.buckets[ip][1])
            return True
        return False
    
    async def __call__(self, request: Request, call_next):
        """Process the request with rate limiting."""
        ip = request.client.host
        
        # Skip rate limiting for certain paths
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            return await call_next(request)
        
        if not self._consume_token(ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests",
                    "retry_after": int(1 / self.tokens_per_second)
                }
            )
        
        return await call_next(request) 