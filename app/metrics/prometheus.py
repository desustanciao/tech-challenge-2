import time

from fastapi import Request
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])

REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "path"])

REQUEST_EXCEPTIONS = Counter("http_request_exceptions_total", "Total HTTP exceptions", ["method", "path", "exception"])


async def prometheus_middleware(request: Request, call_next):
    # Don't instrument metrics endpoint itself
    if request.url.path.startswith("/metrics"):
        return await call_next(request)

    start_time = time.time()

    method = request.method
    route = request.scope.get("route")
    path = route.path if route else request.url.path

    try:
        response = await call_next(request)

        REQUEST_COUNT.labels(method=method, path=path, status=response.status_code).inc()

        return response

    except Exception as e:
        REQUEST_EXCEPTIONS.labels(method=method, path=path, exception=type(e).__name__).inc()
        raise

    finally:
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
