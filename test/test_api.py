import pytest
from fastapi.testclient import TestClient
from main import app
from services import LogService
from datetime import datetime

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health check endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestGetLogs:
    """Test GET /logs endpoint"""

    def test_get_all_logs(self):
        """Test retrieving all logs"""
        response = client.get("/logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

    def test_get_logs_with_level_filter(self):
        """Test filtering logs by level"""
        response = client.get("/logs?level=ERROR")
        assert response.status_code == 200
        data = response.json()
        for log in data["logs"]:
            assert log["level"] == "ERROR"

    def test_get_logs_with_component_filter(self):
        """Test filtering logs by component"""
        response = client.get("/logs?component=UserAuth")
        assert response.status_code == 200
        data = response.json()
        for log in data["logs"]:
            assert log["component"] == "UserAuth"

    def test_get_logs_with_multiple_filters(self):
        """Test filtering logs with multiple criteria"""
        response = client.get("/logs?level=INFO&component=UserAuth")
        assert response.status_code == 200
        data = response.json()
        for log in data["logs"]:
            assert log["level"] == "INFO"
            assert log["component"] == "UserAuth"

    def test_get_logs_with_pagination(self):
        """Test log pagination"""
        response = client.get("/logs?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["logs"]) <= 5

    def test_get_logs_with_start_time(self):
        """Test filtering logs with start_time"""
        response = client.get("/logs?start_time=2025-05-07%2010:00:30")
        assert response.status_code == 200
        data = response.json()
        for log in data["logs"]:
            assert datetime.fromisoformat(log["timestamp"]) >= datetime(
                2025, 5, 7, 10, 0, 30
            )

    def test_get_logs_with_invalid_start_time(self):
        """Test error handling for invalid timestamp"""
        response = client.get("/logs?start_time=invalid_timestamp")
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_get_logs_with_invalid_page_size(self):
        """Test page size validation"""
        response = client.get("/logs?page_size=0")
        assert response.status_code == 422


class TestGetLogStats:
    """Test GET /logs/stats endpoint"""

    def test_get_stats(self):
        """Test retrieving log statistics"""
        response = client.get("/logs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
        assert "level_counts" in data
        assert "component_counts" in data
        assert "time_range" in data

    def test_get_stats_with_time_range(self):
        """Test statistics with time range filter"""
        response = client.get(
            "/logs/stats?start_time=2025-05-07%2010:00:00&end_time=2025-05-07%2010:00:50"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] > 0
        assert "level_counts" in data

    def test_stats_level_counts(self):
        """Test that level counts are correct"""
        response = client.get("/logs/stats")
        assert response.status_code == 200
        data = response.json()
        # Sum of all level counts should equal total entries
        total_from_levels = sum(data["level_counts"].values())
        assert total_from_levels == data["total_entries"]

    def test_stats_component_counts(self):
        """Test that component counts are correct"""
        response = client.get("/logs/stats")
        assert response.status_code == 200
        data = response.json()
        # Sum of all component counts should equal total entries
        total_from_components = sum(data["component_counts"].values())
        assert total_from_components == data["total_entries"]


class TestGetLogById:
    """Test GET /logs/{log_id} endpoint"""

    def test_get_log_by_id(self):
        """Test retrieving a specific log entry"""
        # First, get all logs to find a valid log_id
        response = client.get("/logs")
        assert response.status_code == 200
        logs = response.json()["logs"]

        if logs:
            log_id = logs[0]["log_id"]
            response = client.get(f"/logs/{log_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["log_id"] == log_id
            assert "timestamp" in data
            assert "level" in data
            assert "component" in data
            assert "message" in data

    def test_get_log_by_invalid_id(self):
        """Test error handling for non-existent log ID"""
        response = client.get("/logs/nonexistent_log_id")
        assert response.status_code == 404
        assert "detail" in response.json()


class TestLogService:
    """Test LogService class"""

    def test_log_service_initialization(self):
        """Test LogService initializes correctly"""
        service = LogService(log_directory="logs")
        assert service.logs is not None
        assert len(service.logs) > 0

    def test_filter_by_level(self):
        """Test filtering logs by level"""
        service = LogService(log_directory="logs")
        filtered = service.filter_logs(level="ERROR")
        for log in filtered:
            assert log.level == "ERROR"

    def test_filter_by_component(self):
        """Test filtering logs by component"""
        service = LogService(log_directory="logs")
        filtered = service.filter_logs(component="UserAuth")
        for log in filtered:
            assert log.component == "UserAuth"

    def test_get_log_by_id(self):
        """Test retrieving log by ID"""
        service = LogService(log_directory="logs")
        if service.logs:
            log_id = service.logs[0].log_id
            log = service.get_log_by_id(log_id)
            assert log is not None
            assert log.log_id == log_id

    def test_pagination(self):
        """Test pagination functionality"""
        service = LogService(log_directory="logs")
        paginated, total_pages = service.paginate(service.logs, page=1, page_size=5)
        assert len(paginated) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
