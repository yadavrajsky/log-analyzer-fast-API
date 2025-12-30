# Log File Data Access and Analysis REST API

A production-ready REST API for reading, parsing, and analyzing log files. Built with FastAPI and Python.

## Features

- ✅ Parse and read log files from a specified directory
- ✅ RESTful endpoints for log retrieval and analysis
- ✅ Advanced filtering (by level, component, timestamp range)
- ✅ Statistics and analytics endpoints
- ✅ Pagination support for large datasets
- ✅ Comprehensive error handling
- ✅ Unit tests and documentation
- ✅ Docker support
- ✅ CORS enabled

## Project Structure

```
log_api/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models for request/response validation
├── services.py          # Business logic for log parsing and analysis
├── utils.py             # Utility functions
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore rules
├── logs/                # Directory containing log files
│   ├── sample_2025_05_07.log
│   └── sample_2025_05_08.log
└── tests/               # Unit tests
    ├── __init__.py
    └── test_api.py
```

## Assumptions Made

1. **Log File Format**: Logs are TSV (Tab-Separated Values) with exactly 4 fields: Timestamp, Level, Component, Message
2. **Timestamp Format**: All timestamps follow `YYYY-MM-DD HH:MM:SS` format (ISO 8601 date + time)
3. **Log Directory**: Log files are stored in a `logs/` directory relative to the application root
4. **File Format**: Log files have `.log` extension
5. **Unique IDs**: IDs are generated as `filename_line_number` (e.g., `sample_2025_05_07_0`) for uniqueness
6. **Log Levels**: Expected levels are INFO, WARNING, ERROR, DEBUG, CRITICAL
7. **Pagination**: Default page size is 50 entries, maximum 200
8. **Date Format in API**: Query parameters use ISO format: `2025-05-07 10:00:10`
9. **Case Sensitivity**: Filter parameters are case-sensitive
10. **Large Files**: Application loads all logs into memory during startup for performance; for very large deployments (>1GB), implement database persistence
11. **Concurrency**: Thread-safe implementation suitable for production use
12. **Error Handling**: Returns 400 for client errors, 404 for not found, 500 for server errors

## Installation

### Prerequisites
- Python 3.8+
- pip or poetry

### Setup

1. **Clone the repository**
```bash
git clone <repo-url>
cd log_api
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env if needed (optional, has sensible defaults)
```

5. **Add sample log files**
```bash
# Logs should be placed in the logs/ directory
# Sample logs are provided for testing
```

6. **Run the application**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

## API Endpoints

### 1. Get All Logs
```http
GET /logs
```

**Query Parameters:**
- `level` (optional): Filter by log level (INFO, WARNING, ERROR, DEBUG, CRITICAL)
- `component` (optional): Filter by component name
- `start_time` (optional): Filter logs after this timestamp (format: `2025-05-07 10:00:10`)
- `end_time` (optional): Filter logs before this timestamp
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of entries per page (default: 50, max: 200)

**Example Requests:**
```bash
# Get all logs
curl http://localhost:8000/logs

# Filter by level
curl "http://localhost:8000/logs?level=ERROR"

# Filter by component
curl "http://localhost:8000/logs?component=UserAuth"

# Filter by time range
curl "http://localhost:8000/logs?start_time=2025-05-07%2010:00:10&end_time=2025-05-07%2010:00:25"

# Pagination
curl "http://localhost:8000/logs?page=2&page_size=25"

# Combined filters
curl "http://localhost:8000/logs?level=ERROR&component=Payment&page=1&page_size=20"
```

**Response (200 OK):**
```json
{
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
    },
    {
      "log_id": "sample_2025_05_07_1",
      "timestamp": "2025-05-07T10:00:15",
      "level": "WARNING",
      "component": "GeoIP",
      "message": "Could not resolve IP address '192.168.1.100'."
    }
  ]
}
```

### 2. Get Log Statistics
```http
GET /logs/stats
```

**Query Parameters:**
- `start_time` (optional): Filter stats for logs after this timestamp
- `end_time` (optional): Filter stats for logs before this timestamp

**Example Requests:**
```bash
# Get overall statistics
curl http://localhost:8000/logs/stats

# Statistics for a time range
curl "http://localhost:8000/logs/stats?start_time=2025-05-07%2010:00:00&end_time=2025-05-07%2010:00:30"
```

**Response (200 OK):**
```json
{
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
```

### 3. Get Specific Log Entry
```http
GET /logs/{log_id}
```

**Example Requests:**
```bash
# Get specific log by ID
curl http://localhost:8000/logs/sample_2025_05_07_0
```

**Response (200 OK):**
```json
{
  "log_id": "sample_2025_05_07_0",
  "timestamp": "2025-05-07T10:00:00",
  "level": "INFO",
  "component": "UserAuth",
  "message": "User 'john.doe' logged in successfully."
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Log entry with ID 'invalid_id' not found"
}
```

## Error Handling

The API returns appropriate HTTP status codes:

| Status Code | Scenario |
|------------|----------|
| 200 | Successful request |
| 400 | Invalid query parameters (e.g., bad timestamp format) |
| 404 | Log entry not found |
| 422 | Validation error |
| 500 | Server error |

**Error Response Format:**
```json
{
  "detail": "Description of the error"
}
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

## Docker Support

Build and run with Docker:

```bash
# Build image
docker build -t log-api .

# Run container
docker run -p 8000:8000 -v $(pwd)/logs:/app/logs log-api
```

## Performance Considerations

1. **Caching**: Logs are loaded and cached in memory at startup
2. **Pagination**: Default 50 items per page to reduce payload size
3. **Filtering**: Done in-memory; for very large datasets (>100k entries), consider database persistence
4. **Index**: Component and level indices maintained for faster filtering

## Production Deployment

For production use:

1. Use a production ASGI server (Gunicorn with Uvicorn workers):
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

2. Enable HTTPS with a reverse proxy (Nginx/Apache)
3. Add authentication/authorization (JWT tokens)
4. Use a database (PostgreSQL/MongoDB) for persistent storage
5. Implement logging to external service
6. Add rate limiting

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **python-dateutil**: Date/time utilities
- **pytest**: Testing framework
- **httpx**: HTTP client for testing

## License

MIT

## Support

For issues or questions, please create an issue in the repository.

---

**Last Updated**: December 30, 2025
**Version**: 1.0.0
