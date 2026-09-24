import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from app.core.config import settings

class InMemoryRateLimiter:
    """
    In-memory timestamp-based sliding-window rate limiter for protecting endpoints from brute-force/abuse.
    Suitable for single-instance protection.
    
    Identifies clients by their IP address (falling back to 127.0.0.1).
    Throws a 429 Too Many Requests if limits are exceeded.
    """
    
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self._history: dict[str, list[float]] = defaultdict(list)
    
    def __call__(self, request: Request):
        if not self.requests or not self.window:
            return  # Limiting disabled
            
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        
        # Prune old requests
        window_start = now - self.window
        self._history[client_ip] = [ts for ts in self._history[client_ip] if ts > window_start]
        
        if len(self._history[client_ip]) >= self.requests:
            retry_after = int(self.window - (now - self._history[client_ip][0]))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests",
                headers={"Retry-After": str(max(1, retry_after))}
            )
            
        self._history[client_ip].append(now)

    def reset(self):
        """Used strictly in tests to isolate test cases."""
        self._history.clear()

auth_rate_limit = InMemoryRateLimiter(
    requests=settings.AUTH_RATE_LIMIT_REQUESTS,
    window=settings.AUTH_RATE_LIMIT_WINDOW
)

disease_rate_limit = InMemoryRateLimiter(
    requests=settings.DISEASE_RATE_LIMIT_REQUESTS,
    window=settings.DISEASE_RATE_LIMIT_WINDOW
)
