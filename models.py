from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class LogEntry(BaseModel):
    """Represents a single log entry"""
    log_id: str = Field(..., description="Unique identifier for the log entry")
    timestamp: datetime = Field(..., description="Timestamp of the log entry")
    level: str = Field(..., description="Log level (INFO, WARNING, ERROR, DEBUG, CRITICAL)")
    component: str = Field(..., description="Component that generated the log")
    message: str = Field(..., description="Log message")

    class Config:
        json_schema_extra = {
            "example": {
                "log_id": "sample_2025_05_07_0",
                "timestamp": "2025-05-07T10:00:00",
                "level": "INFO",
                "component": "UserAuth",
                "message": "User 'john.doe' logged in successfully."
            }
        }


class LogsResponse(BaseModel):
    """Response model for GET /logs endpoint"""
    total: int = Field(..., description="Total number of matching log entries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of entries per page")
    total_pages: int = Field(..., description="Total number of pages")
    logs: List[LogEntry] = Field(..., description="List of log entries")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 4,
                "page": 1,
                "page_size": 50,
                "total_pages": 1,
                "logs": [
                    {
                        "log_id": "sample_2025_05_07_0",
                        "timestamp": "2025-05-07T10:00:00",
                        "level": "INFO",
                        "component": "UserAuth",
                        "message": "User 'john.doe' logged in successfully."
                    }
                ]
            }
        }


class LogStatsResponse(BaseModel):
    """Response model for GET /logs/stats endpoint"""
    total_entries: int = Field(..., description="Total number of log entries")
    level_counts: Dict[str, int] = Field(..., description="Count of logs per level")
    component_counts: Dict[str, int] = Field(..., description="Count of logs per component")
    time_range: Dict[str, Optional[datetime]] = Field(..., description="Min and max timestamps")

    class Config:
        json_schema_extra = {
            "example": {
                "total_entries": 4,
                "level_counts": {
                    "INFO": 2,
                    "WARNING": 1,
                    "ERROR": 1
                },
                "component_counts": {
                    "UserAuth": 2,
                    "GeoIP": 1,
                    "Payment": 1
                },
                "time_range": {
                    "earliest": "2025-05-07T10:00:00",
                    "latest": "2025-05-07T10:00:25"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error responses"""
    detail: str = Field(..., description="Error message")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid timestamp format. Expected format: YYYY-MM-DD HH:MM:SS"
            }
        }
