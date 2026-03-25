"""
MongoDB models and schemas for the application.
Defines data structures for tests, metrics, and analytics.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update(type="string")
        return schema


class TestStatus(str, Enum):
    """Status of a load test."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class HTTPMethod(str, Enum):
    """HTTP methods supported."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"


# ==================== Test Configuration ====================

class URLConfig(BaseModel):
    """Configuration for a single URL target."""
    url: str = Field(..., description="Target URL")
    method: HTTPMethod = Field(default=HTTPMethod.GET, description="HTTP method")
    weight: float = Field(default=1.0, ge=0.1, le=100.0, description="Traffic weight")
    timeout: int = Field(default=10, ge=1, le=120, description="Request timeout in seconds")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    body: Optional[str] = Field(default=None, description="Request body for POST/PUT")


class LoadTestConfig(BaseModel):
    """Configuration for load test execution."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    urls: List[URLConfig] = Field(..., min_items=1, description="URLs to test")
    duration: int = Field(default=60, ge=10, le=3600, description="Test duration in seconds")
    concurrency: int = Field(default=10, ge=1, le=1000, description="Concurrent connections")
    ramp_up: int = Field(default=10, ge=0, le=300, description="Ramp-up time in seconds")
    retry_count: int = Field(default=1, ge=0, le=5, description="Retry attempts per request")
    think_time: float = Field(default=0, ge=0, le=10, description="Delay between requests per VU")


# ==================== Test Results ====================

class PerSecondMetrics(BaseModel):
    """Metrics recorded per second during test."""
    timestamp: datetime
    requests_sent: int
    requests_succeeded: int
    requests_failed: int
    rps: float  # Requests per second
    min_latency: float
    avg_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    max_latency: float


class TestResultSummary(BaseModel):
    """Summary statistics for a completed test."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_rps: float
    peak_rps: float
    total_data_received: int  # bytes
    min_latency: float  # milliseconds
    avg_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    max_latency: float
    error_distribution: Dict[str, int]  # error_type: count


# ==================== Database Models ====================

class LoadTest(BaseModel):
    """Main LoadTest document."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: Optional[str] = Field(default=None)
    config: LoadTestConfig
    status: TestStatus = Field(default=TestStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    summary: Optional[TestResultSummary] = None
    per_second_metrics: List[PerSecondMetrics] = Field(default_factory=list)
    
    # Error details
    error_message: Optional[str] = None
    
    # Worker info
    worker_id: Optional[str] = None
    
    class Config:
        populated_by_name = True
        arbitrary_types_allowed = True


class TestData(BaseModel):
    """Test data for MongoDB storage."""
    config: dict
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    summary: Optional[dict] = None
    per_second_metrics: list = []
    error_message: Optional[str] = None
    worker_id: Optional[str] = None


# ==================== Request/Response Models ====================

class CreateTestRequest(BaseModel):
    """Request to create a new test."""
    name: str
    description: Optional[str] = None
    urls: List[URLConfig]
    duration: int = 60
    concurrency: int = 10
    ramp_up: int = 10
    retry_count: int = 1
    think_time: float = 0


class TestResponse(BaseModel):
    """Response containing test details."""
    id: str = Field(alias="_id")
    config: LoadTestConfig
    status: TestStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    summary: Optional[TestResultSummary]
    error_message: Optional[str]
    
    class Config:
        populate_by_name = True


class ListTestsResponse(BaseModel):
    """Response for listing tests."""
    total: int
    page: int
    page_size: int
    tests: List[TestResponse]


class WebsiteAnalysisResult(BaseModel):
    """Result of website analysis."""
    url: str
    title: Optional[str]
    description: Optional[str]
    tech_stack: List[str]
    emails: List[str]
    social_links: Dict[str, str]
    scripts: List[str]
    performance_hints: List[str]
    ai_summary: str
    analyzed_at: datetime
