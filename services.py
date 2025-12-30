import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from models import LogEntry

class LogService:
    """Service class for log file parsing and analysis"""
    
    def __init__(self, log_directory: str = "logs"):
        """
        Initialize the log service.
        
        Args:
            log_directory: Directory containing log files
        """
        self.log_directory = log_directory
        self.logs: List[LogEntry] = []
        self.log_index: Dict[str, LogEntry] = {}
        self.component_index: Dict[str, List[LogEntry]] = defaultdict(list)
        self.level_index: Dict[str, List[LogEntry]] = defaultdict(list)
        self._ensure_directory_exists()
        self._load_logs()
    
    def _ensure_directory_exists(self) -> None:
        """Ensure the log directory exists"""
        Path(self.log_directory).mkdir(parents=True, exist_ok=True)
    
    def _load_logs(self) -> None:
        """Load and parse all log files from the directory"""
        self.logs.clear()
        self.log_index.clear()
        self.component_index.clear()
        self.level_index.clear()
        
        log_files = sorted(Path(self.log_directory).glob("*.log"))
        
        for log_file in log_files:
            self._parse_log_file(log_file)
    
    def _parse_log_file(self, file_path: Path) -> None:
        """
        Parse a single log file and populate the logs list.
        
        Args:
            file_path: Path to the log file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    try:
                        log_entry = self._parse_log_line(line, file_path.stem, line_num)
                        if log_entry:
                            self.logs.append(log_entry)
                            self.log_index[log_entry.log_id] = log_entry
                            self.component_index[log_entry.component].append(log_entry)
                            self.level_index[log_entry.level].append(log_entry)
                    except ValueError as e:
                        print(f"Warning: Skipping invalid line {line_num + 1} in {file_path.name}: {str(e)}")
        except IOError as e:
            print(f"Error reading file {file_path}: {str(e)}")
    
    def _parse_log_line(self, line: str, filename: str, line_num: int) -> Optional[LogEntry]:
        """
        Parse a single log line.
        
        Args:
            line: The log line to parse
            filename: Name of the file (without extension)
            line_num: Line number in the file
        
        Returns:
            LogEntry if successfully parsed, None otherwise
        
        Raises:
            ValueError: If the line cannot be parsed
        """
        parts = line.split('\t')
        
        if len(parts) < 4:
            raise ValueError(f"Expected at least 4 tab-separated fields, got {len(parts)}")
        
        timestamp_str = parts[0]
        level = parts[1].strip()
        component = parts[2].strip()
        message = parts[3].strip()
        
        # Parse timestamp
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}. Expected: YYYY-MM-DD HH:MM:SS")
        
        # Generate unique ID
        log_id = f"{filename}_{line_num}"
        
        return LogEntry(
            log_id=log_id,
            timestamp=timestamp,
            level=level,
            component=component,
            message=message
        )
    
    def get_all_logs(self) -> List[LogEntry]:
        """Get all log entries"""
        return self.logs.copy()
    
    def get_log_by_id(self, log_id: str) -> Optional[LogEntry]:
        """Get a specific log entry by ID"""
        return self.log_index.get(log_id)
    
    def filter_logs(
        self,
        level: Optional[str] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[LogEntry]:
        """
        Filter logs based on criteria.
        
        Args:
            level: Filter by log level
            component: Filter by component
            start_time: Filter logs after this timestamp (inclusive)
            end_time: Filter logs before this timestamp (inclusive)
        
        Returns:
            List of filtered log entries
        """
        filtered = self.logs.copy()
        
        if level:
            filtered = [log for log in filtered if log.level == level]
        
        if component:
            filtered = [log for log in filtered if log.component == component]
        
        if start_time:
            filtered = [log for log in filtered if log.timestamp >= start_time]
        
        if end_time:
            filtered = [log for log in filtered if log.timestamp <= end_time]
        
        return filtered
    
    def get_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """
        Get statistics about the logs.
        
        Args:
            start_time: Filter stats for logs after this timestamp
            end_time: Filter stats for logs before this timestamp
        
        Returns:
            Dictionary containing statistics
        """
        filtered_logs = self.filter_logs(start_time=start_time, end_time=end_time)
        
        level_counts = defaultdict(int)
        component_counts = defaultdict(int)
        
        for log in filtered_logs:
            level_counts[log.level] += 1
            component_counts[log.component] += 1
        
        earliest = None
        latest = None
        
        if filtered_logs:
            sorted_logs = sorted(filtered_logs, key=lambda x: x.timestamp)
            earliest = sorted_logs[0].timestamp
            latest = sorted_logs[-1].timestamp
        
        return {
            "total_entries": len(filtered_logs),
            "level_counts": dict(level_counts),
            "component_counts": dict(component_counts),
            "time_range": {
                "earliest": earliest,
                "latest": latest
            }
        }
    
    def paginate(
        self,
        items: List[LogEntry],
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[LogEntry], int]:
        """
        Paginate a list of items.
        
        Args:
            items: List of items to paginate
            page: Page number (1-indexed)
            page_size: Number of items per page
        
        Returns:
            Tuple of (paginated_items, total_pages)
        """
        total_pages = (len(items) + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return items[start_idx:end_idx], total_pages
    
    def reload_logs(self) -> None:
        """Reload logs from disk"""
        self._load_logs()
