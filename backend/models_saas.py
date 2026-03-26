"""
Enhanced models for SaaS: Auth, Subscriptions, Tests, Metrics, AI Analysis
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)


# ==================== Enums ====================

class PlanType(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    PRO = "pro"


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class UserRole(str, Enum):
    """User roles."""
    USER = "user"
    ADMIN = "admin"


# ==================== Auth Models ====================

class UserCreate(BaseModel):
    """User registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str


class UserLogin(BaseModel):
    """User login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class PasswordChangeRequest(BaseModel):
    """Change password."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class User(BaseModel):
    """User model."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    password_hash: str
    name: str
    role: UserRole = UserRole.USER
    plan: PlanType = PlanType.FREE
    plan_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        populate_by_name = True


class UserProfile(BaseModel):
    """Public user info."""
    email: str
    name: str
    plan: PlanType
    plan_expires: Optional[datetime]
    created_at: datetime


# ==================== Subscription Models ====================

class PlanLimits(BaseModel):
    """Plan feature limits."""
    daily_test_limit: int
    max_concurrency: int
    max_duration: int  # seconds
    export_formats: List[str]  # ["json", "csv"]


PLAN_LIMITS = {
    PlanType.FREE: PlanLimits(
        daily_test_limit=2,
        max_concurrency=10,
        max_duration=60,
        export_formats=["json"]
    ),
    PlanType.PRO: PlanLimits(
        daily_test_limit=999999,
        max_concurrency=1000,
        max_duration=3600,
        export_formats=["json", "csv"]
    )
}


class Subscription(BaseModel):
    """Subscription model."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    plan: PlanType
    tests_used_today: int = 0
    last_reset: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class PaymentRequest(BaseModel):
    """Dummy payment request."""
    user_id: str
    plan: PlanType
    amount: float


class PaymentResponse(BaseModel):
    """Dummy payment response."""
    success: bool
    message: str
    plan_expires: Optional[datetime]


# ==================== Test & Metrics Models ====================

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class URLConfig(BaseModel):
    """URL configuration for load test."""
    url: str
    method: HTTPMethod = HTTPMethod.GET
    weight: float = 1.0
    timeout: int = 10
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Optional[str] = None


class LoadTestConfig(BaseModel):
    """Load test configuration."""
    name: str
    urls: List[URLConfig]
    duration: int = 60
    concurrency: int = 10
    ramp_up: int = 0
    retry_count: int = 1
    think_time: float = 0


class CreateTestRequest(BaseModel):
    """Create test request."""
    name: str
    urls: List[URLConfig]
    duration: int = 60
    concurrency: int = 10
    ramp_up: int = 0


class PerSecondMetrics(BaseModel):
    """Per-second metrics."""
    timestamp: datetime
    requests_sent: int
    requests_succeeded: int
    requests_failed: int
    rps: float
    min_latency: float
    avg_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    max_latency: float


class TestResultSummary(BaseModel):
    """Test result summary."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    avg_rps: float
    peak_rps: float
    total_data_received: int
    min_latency: float
    avg_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    max_latency: float
    error_distribution: Dict[str, int]


class LoadTest(BaseModel):
    """Load test document."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    config: LoadTestConfig
    status: TestStatus = TestStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    summary: Optional[TestResultSummary] = None
    per_second_metrics: List[Dict] = Field(default_factory=list)
    error_message: Optional[str] = None

    class Config:
        populate_by_name = True


# ==================== AI Analysis Models ====================

class AIAnalysisRequest(BaseModel):
    """AI website analysis request."""
    url: str


class AIAnalysisResult(BaseModel):
    """AI analysis result."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    url: str
    tech_stack: List[str]
    meta_description: Optional[str]
    emails: List[str]
    social_links: Dict[str, str]
    grock_summary: str
    seo_score: int
    performance_score: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# ==================== Response Models ====================

class TestDetailResponse(BaseModel):
    """Test detail response."""
    id: str
    user_id: str
    config: LoadTestConfig
    status: TestStatus
    created_at: datetime
    completed_at: Optional[datetime]
    summary: Optional[TestResultSummary]
    metrics: List[Dict]


class UserStatsResponse(BaseModel):
    """User statistics."""
    total_tests: int
    tests_today: int
    plan: PlanType
    plan_expires: Optional[datetime]
    daily_limit: int
    remaining_tests: int


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    name: str
    plan: str
    plan_expires: Optional[datetime]
    role: str
    is_active: bool
    created_at: datetime
    tests_used_today: int
