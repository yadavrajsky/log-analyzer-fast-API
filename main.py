from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime

from config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    LOG_DIRECTORY,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
)
from services import LogService
from models import LogEntry, LogsResponse, LogStatsResponse, ErrorResponse
from utils import parse_timestamp, validate_page_size, validate_page_number

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Initialize log service
log_service = LogService(log_directory=LOG_DIRECTORY)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_logs_loaded": len(log_service.logs),
        "app_version": APP_VERSION,
    }


# ============================================================================
# GET /logs - Retrieve all logs with optional filtering and pagination
# ============================================================================


@app.get(
    "/logs",
    response_model=LogsResponse,
    responses={
        200: {"description": "Successfully retrieved logs"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    tags=["Logs"],
)
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    component: Optional[str] = Query(None, description="Filter by component"),
    start_time: Optional[str] = Query(
        None,
        description="Filter logs after this timestamp (format: YYYY-MM-DD HH:MM:SS)",
    ),
    end_time: Optional[str] = Query(
        None,
        description="Filter logs before this timestamp (format: YYYY-MM-DD HH:MM:SS)",
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        description=f"Number of entries per page (max: {MAX_PAGE_SIZE})",
    ),
):
    """
    Retrieve all log entries with optional filtering.

    Query Parameters:
    - **level**: Filter by log level (e.g., INFO, WARNING, ERROR)
    - **component**: Filter by component name
    - **start_time**: Filter logs after this timestamp (format: YYYY-MM-DD HH:MM:SS)
    - **end_time**: Filter logs before this timestamp (format: YYYY-MM-DD HH:MM:SS)
    - **page**: Page number for pagination (default: 1)
    - **page_size**: Entries per page (default: 50, max: 200)
    """
    try:
        # Validate pagination parameters
        page = validate_page_number(page)
        page_size = validate_page_size(page_size, MAX_PAGE_SIZE)

        # Parse timestamps if provided
        start_dt = None
        end_dt = None

        if start_time:
            try:
                start_dt = parse_timestamp(start_time)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        if end_time:
            try:
                end_dt = parse_timestamp(end_time)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Validate time range
        if start_dt and end_dt and start_dt > end_dt:
            raise HTTPException(
                status_code=400, detail="start_time cannot be after end_time"
            )

        # Filter logs
        filtered_logs = log_service.filter_logs(
            level=level, component=component, start_time=start_dt, end_time=end_dt
        )

        # Paginate results
        paginated_logs, total_pages = log_service.paginate(
            filtered_logs, page, page_size
        )

        # Return response
        return LogsResponse(
            total=len(filtered_logs),
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            logs=paginated_logs,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# GET /logs/stats - Get statistics about logs
# ============================================================================


@app.get(
    "/logs/stats",
    response_model=LogStatsResponse,
    responses={
        200: {"description": "Successfully retrieved statistics"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    tags=["Logs"],
)
async def get_logs_stats(
    start_time: Optional[str] = Query(
        None,
        description="Filter stats for logs after this timestamp (format: YYYY-MM-DD HH:MM:SS)",
    ),
    end_time: Optional[str] = Query(
        None,
        description="Filter stats for logs before this timestamp (format: YYYY-MM-DD HH:MM:SS)",
    ),
):
    """
    Get statistics about log entries.

    Returns:
    - Total number of log entries
    - Count of logs per level
    - Count of logs per component
    - Time range (earliest and latest timestamps)
    """
    try:
        # Parse timestamps if provided
        start_dt = None
        end_dt = None

        if start_time:
            try:
                start_dt = parse_timestamp(start_time)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        if end_time:
            try:
                end_dt = parse_timestamp(end_time)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Validate time range
        if start_dt and end_dt and start_dt > end_dt:
            raise HTTPException(
                status_code=400, detail="start_time cannot be after end_time"
            )

        # Get statistics
        stats = log_service.get_statistics(start_time=start_dt, end_time=end_dt)

        # Convert to response model
        return LogStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# GET /logs/{log_id} - Get a specific log entry
# ============================================================================


@app.get(
    "/logs/{log_id}",
    response_model=LogEntry,
    responses={
        200: {"description": "Successfully retrieved log entry"},
        404: {"model": ErrorResponse, "description": "Log entry not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    tags=["Logs"],
)
async def get_log_by_id(log_id: str):
    """
    Retrieve a specific log entry by its ID.

    Args:
    - **log_id**: Unique identifier of the log entry (format: filename_line_number)

    Example:
    - GET /logs/sample_2025_05_07_0
    """
    try:
        log_entry = log_service.get_log_by_id(log_id)

        if not log_entry:
            raise HTTPException(
                status_code=404, detail=f"Log entry with ID '{log_id}' not found"
            )

        return log_entry

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["Info"])
async def root():
    """API root endpoint with information"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "GET /logs": "Retrieve all logs with optional filtering and pagination",
            "GET /logs/stats": "Get statistics about logs",
            "GET /logs/{log_id}": "Get a specific log entry by ID",
        },
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print(f"✓ {APP_NAME} v{APP_VERSION} started")
    print(f"✓ Log directory: {LOG_DIRECTORY}")
    print(f"✓ Total logs loaded: {len(log_service.logs)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"✓ {APP_NAME} v{APP_VERSION} shutdown")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
