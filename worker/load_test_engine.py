"""
Core load testing engine using asyncio and aiohttp.
Handles concurrent HTTP requests, metrics collection, and reporting.
"""

import asyncio
import aiohttp
import logging
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics
import json

logger = logging.getLogger(__name__)


class HTTPMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"


@dataclass
class RequestConfig:
    """Configuration for a single request type."""
    url: str
    method: HTTPMethod = HTTPMethod.GET
    weight: float = 1.0
    timeout: int = 10
    headers: Dict = field(default_factory=dict)
    body: Optional[str] = None


@dataclass
class PerSecondMetrics:
    """Metrics collected per second."""
    timestamp: int
    requests_sent: int = 0
    requests_succeeded: int = 0
    requests_failed: int = 0
    latencies: List[float] = field(default_factory=list)
    errors: Dict[str, int] = field(default_factory=dict)
    
    def calculate_stats(self) -> dict:
        """Calculate statistics from collected latencies."""
        if not self.latencies:
            return {
                "rps": 0,
                "min_latency": 0,
                "avg_latency": 0,
                "p50_latency": 0,
                "p95_latency": 0,
                "p99_latency": 0,
                "max_latency": 0
            }
        
        sorted_latencies = sorted(self.latencies)
        
        return {
            "rps": self.requests_succeeded,
            "min_latency": min(self.latencies),
            "avg_latency": statistics.mean(self.latencies),
            "p50_latency": self._percentile(sorted_latencies, 50),
            "p95_latency": self._percentile(sorted_latencies, 95),
            "p99_latency": self._percentile(sorted_latencies, 99),
            "max_latency": max(self.latencies)
        }
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        index = (percentile / 100.0) * (len(data) - 1)
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(data):
            return data[lower]
        
        weight = index - lower
        return data[lower] * (1 - weight) + data[upper] * weight


@dataclass
class TestResult:
    """Final test results."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    latencies: List[float] = field(default_factory=list)
    all_errors: Dict[str, int] = field(default_factory=dict)
    error_details: List[Dict] = field(default_factory=list)
    
    def calculate_summary(self) -> dict:
        """Calculate final summary statistics."""
        if not self.latencies:
            return self._empty_summary()
        
        sorted_latencies = sorted(self.latencies)
        success_rate = (self.successful_requests / self.total_requests * 100) \
            if self.total_requests > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(success_rate, 2),
            "avg_rps": max(self.successful_requests / 300, 0) if hasattr(self, 'duration') else 0,
            "peak_rps": 0,
            "total_data_received": 0,
            "min_latency": min(self.latencies),
            "avg_latency": sum(self.latencies) / len(self.latencies),
            "p50_latency": self._percentile(sorted_latencies, 50),
            "p95_latency": self._percentile(sorted_latencies, 95),
            "p99_latency": self._percentile(sorted_latencies, 99),
            "max_latency": max(self.latencies),
            "error_distribution": self.all_errors
        }
    
    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        index = (percentile / 100.0) * (len(data) - 1)
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(data):
            return data[lower]
        
        weight = index - lower
        return data[lower] * (1 - weight) + data[upper] * weight
    
    @staticmethod
    def _empty_summary() -> dict:
        """Return empty summary when no data."""
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "success_rate": 0,
            "avg_rps": 0,
            "peak_rps": 0,
            "total_data_received": 0,
            "min_latency": 0,
            "avg_latency": 0,
            "p50_latency": 0,
            "p95_latency": 0,
            "p99_latency": 0,
            "max_latency": 0,
            "error_distribution": {}
        }


class LoadTestEngine:
    """
    Main async load testing engine.
    Orchestrates concurrent requests and metrics collection.
    """
    
    def __init__(
        self,
        configs: List[RequestConfig],
        concurrency: int,
        duration: int,
        ramp_up: int = 0,
        retry_count: int = 1,
        think_time: float = 0.0
    ):
        """
        Initialize load test engine.
        
        Args:
            configs: List of request configurations (with weights)
            concurrency: Number of concurrent connections
            duration: Test duration in seconds
            ramp_up: Ramp-up time in seconds
            retry_count: Number of retries per request
            think_time: Delay between requests per virtual user
        """
        self.configs = configs
        self.concurrency = concurrency
        self.duration = duration
        self.ramp_up = ramp_up
        self.retry_count = retry_count
        self.think_time = think_time
        
        self.result = TestResult()
        self.per_second_metrics: Dict[int, PerSecondMetrics] = {}
        
        # Calculate weights
        self._calculate_weights()
    
    def _calculate_weights(self):
        """Calculate normalized weights for URL selection."""
        total_weight = sum(config.weight for config in self.configs)
        for config in self.configs:
            config.weight = config.weight / total_weight
    
    async def run(self, progress_callback=None) -> TestResult:
        """
        Execute the load test.
        
        Args:
            progress_callback: Optional callback for progress updates
        
        Returns:
            TestResult with all collected metrics
        """
        logger.info(f"Starting load test: {self.concurrency} VU, {self.duration}s duration")
        
        start_time = time.time()
        connector = aiohttp.TCPConnector(limit=self.concurrency * 2)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Create tasks for all virtual users
            tasks = [
                self._run_virtual_user(session, start_time, progress_callback)
                for _ in range(self.concurrency)
            ]
            
            # Run all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Load test completed")
        return self.result
    
    async def _run_virtual_user(self, session: aiohttp.ClientSession, start_time: float, progress_callback):
        """Run requests from a single virtual user."""
        vuser_start = time.time()
        
        while True:
            current_time = time.time() - start_time
            
            # Check if test duration exceeded
            if current_time > self.duration:
                break
            
            # Ramp-up logic
            if self.ramp_up > 0:
                users_at_this_time = (current_time / self.ramp_up) * self.concurrency
                vuser_id = int(vuser_start % self.concurrency)
                if vuser_id > users_at_this_time:
                    await asyncio.sleep(0.1)
                    continue
            
            # Select a URL based on weights
            config = self._select_config()
            
            # Make request
            latency = await self._make_request(session, config)
            
            # Record metrics
            second = int(current_time)
            if second not in self.per_second_metrics:
                self.per_second_metrics[second] = PerSecondMetrics(timestamp=second)
            
            # Think time
            if self.think_time > 0:
                await asyncio.sleep(self.think_time)
            
            # Report progress
            if progress_callback:
                await progress_callback(self.result, self.per_second_metrics)
    
    def _select_config(self) -> RequestConfig:
        """Select a URL configuration based on weights."""
        import random
        r = random.random()
        cumulative = 0.0
        
        for config in self.configs:
            cumulative += config.weight
            if r < cumulative:
                return config
        
        return self.configs[-1]
    
    async def _make_request(self, session: aiohttp.ClientSession, config: RequestConfig) -> float:
        """
        Make an HTTP request with retry logic.
        
        Returns:
            Latency in milliseconds
        """
        for attempt in range(self.retry_count + 1):
            try:
                start = time.time()
                
                async with session.request(
                    method=config.method.value,
                    url=config.url,
                    headers=config.headers,
                    data=config.body,
                    timeout=aiohttp.ClientTimeout(total=config.timeout),
                    ssl=False
                ) as response:
                    latency_ms = (time.time() - start) * 1000
                    
                    # Read response to ensure connection is used
                    await response.read()
                    
                    # Record success
                    self.result.total_requests += 1
                    self.result.successful_requests += 1
                    self.result.latencies.append(latency_ms)
                    
                    return latency_ms
            
            except asyncio.TimeoutError:
                error_type = "timeout"
                if attempt == self.retry_count:
                    self.result.total_requests += 1
                    self.result.failed_requests += 1
                    self.result.all_errors[error_type] = self.result.all_errors.get(error_type, 0) + 1
                    self.result.error_details.append({
                        "url": config.url,
                        "error": error_type,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            except aiohttp.ClientError as e:
                error_type = type(e).__name__
                if attempt == self.retry_count:
                    self.result.total_requests += 1
                    self.result.failed_requests += 1
                    self.result.all_errors[error_type] = self.result.all_errors.get(error_type, 0) + 1
                    self.result.error_details.append({
                        "url": config.url,
                        "error": error_type,
                        "details": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            except Exception as e:
                error_type = "unknown"
                if attempt == self.retry_count:
                    self.result.total_requests += 1
                    self.result.failed_requests += 1
                    self.result.all_errors[error_type] = self.result.all_errors.get(error_type, 0) + 1
            
            # Exponential backoff for retries
            if attempt < self.retry_count:
                await asyncio.sleep(2 ** attempt * 0.1)
        
        return 0.0
