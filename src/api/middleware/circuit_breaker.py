from enum import Enum
import time
import asyncio
from typing import Dict, Callable, Any, Optional
from loguru import logger

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker for protecting external service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_timeout: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_timeout = half_open_timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0
        self.last_test_time = 0
    
    def _should_allow_request(self) -> bool:
        """Determine if a request should be allowed based on circuit state."""
        current_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            if current_time - self.last_failure_time > self.recovery_timeout:
                logger.info("Circuit transitioning to HALF_OPEN state")
                self.state = CircuitState.HALF_OPEN
                self.last_test_time = current_time
                return True
            return False
            
        # HALF_OPEN state
        if current_time - self.last_test_time > self.half_open_timeout:
            logger.info("Circuit transitioning back to CLOSED state")
            self.state = CircuitState.CLOSED
            self.failures = 0
            return True
            
        return False
    
    def record_failure(self):
        """Record a failure and potentially open the circuit."""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN or self.failures >= self.failure_threshold:
            logger.warning("Circuit transitioning to OPEN state")
            self.state = CircuitState.OPEN
    
    def record_success(self):
        """Record a success and potentially close the circuit."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit transitioning back to CLOSED state")
            self.state = CircuitState.CLOSED
            self.failures = 0

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create a circuit breaker for a service."""
        if service_name not in self._breakers:
            self._breakers[service_name] = CircuitBreaker()
        return self._breakers[service_name]
    
    async def call_with_circuit_breaker(
        self,
        service_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Call a function with circuit breaker protection."""
        breaker = self.get_breaker(service_name)
        
        if not breaker._should_allow_request():
            raise ServiceUnavailableError(f"Circuit breaker open for {service_name}")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            breaker.record_success()
            return result
        except Exception as e:
            breaker.record_failure()
            raise ServiceError(f"Service {service_name} call failed: {str(e)}")

class ServiceError(Exception):
    """Base exception for service errors."""
    pass

class ServiceUnavailableError(ServiceError):
    """Raised when a service is unavailable due to circuit breaker."""
    pass 