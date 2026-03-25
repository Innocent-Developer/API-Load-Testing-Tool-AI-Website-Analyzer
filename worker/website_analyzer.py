"""
AI Website Analyzer module.
Analyzes websites for tech stack, SEO, performance, and generates AI summaries.
"""

import re
import asyncio
import logging
from typing import List, Dict, Set, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class WebsiteAnalyzer:
    """
    Comprehensive website analyzer.
    Detects tech stack, SEO metrics, extracts information, and generates AI summaries.
    """
    
    # Tech stack signatures
    TECH_SIGNATURES = {
        "React": [
            r"react\.js",
            r"__REACT",
            r'"react"',
            r"next\.js",
        ],
        "Vue": [
            r"vue\.js",
            r"__VUE__",
            r'"vue"',
        ],
        "Angular": [
            r"angular\.js",
            r"__ANGULAR__",
            r"ng-app",
        ],
        "jQuery": [
            r"jquery",
            r"jQuery",
        ],
        "Bootstrap": [
            r"bootstrap",
            r"_assets.*bootstrap",
        ],
        "Tailwind": [
            r"tailwind",
            r"_next.*static",
        ],
        "Next.js": [
            r"next\.js",
            r"__NEXT_DATA__",
            r"_next/",
        ],
        "Nuxt": [
            r"nuxt",
            r"__NUXT__",
        ],
        "Svelte": [
            r"svelte",
        ],
        "TypeScript": [
            r"\.ts",
            r"typescript",
        ],
        "Node.js": [
            r"node",
            r"express",
        ],
        "Python/Django": [
            r"django",
            r"csrf",
            r"django-admin",
        ],
        "Flask": [
            r"flask",
        ],
        "FastAPI": [
            r"fastapi",
        ],
        "WordPress": [
            r"wp-content",
            r"wp-includes",
            r"wordpress",
        ],
    }
    
    # Email pattern
    EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    
    # Social media patterns
    SOCIAL_PATTERNS = {
        "twitter": r"(https?://)?(www\.)?twitter\.com/[\w\-]+",
        "linkedin": r"(https?://)?(www\.)?linkedin\.com/(in|company)/[\w\-]+",
        "github": r"(https?://)?(www\.)?github\.com/[\w\-]+",
        "facebook": r"(https?://)?(www\.)?facebook\.com/[\w\-]+",
        "instagram": r"(https?://)?(www\.)?instagram\.com/[\w\-]+",
        "youtube": r"(https?://)?(www\.)?youtube\.com/(c|channel|user)/[\w\-]+",
    }
    
    def __init__(self, timeout: int = 10):
        """
        Initialize analyzer.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    async def analyze(self, url: str) -> Dict:
        """
        Analyze a website comprehensively.
        
        Args:
            url: Website URL to analyze
        
        Returns:
            Analysis result with all collected data
        """
        logger.info(f"Analyzing: {url}")
        
        try:
            # Fetch HTML
            html_content, headers = await self._fetch_html(url)
            if not html_content:
                return self._error_response(url, "Failed to fetch website")
            
            # Parse HTML
            soup = BeautifulSoup(html_content, "lxml")
            
            # Extract data
            title = self._extract_title(soup)
            description = self._extract_description(soup)
            tech_stack = self._detect_tech_stack(html_content, headers)
            emails = self._extract_emails(html_content)
            social_links = self._extract_social_links(html_content)
            scripts = self._extract_scripts(soup)
            performance_hints = self._analyze_performance(soup, html_content, headers)
            ai_summary = self._generate_ai_summary(
                title, description, tech_stack, performance_hints
            )
            
            return {
                "url": url,
                "status": "success",
                "title": title,
                "description": description,
                "tech_stack": tech_stack,
                "emails": emails,
                "social_links": social_links,
                "scripts": scripts,
                "performance_hints": performance_hints,
                "ai_summary": ai_summary,
                "analyzed_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return self._error_response(url, str(e))
    
    async def _fetch_html(self, url: str) -> tuple:
        """Fetch HTML content from URL."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=False,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                ) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None, {}
                    
                    content = await response.text()
                    headers = dict(response.headers)
                    
                    return content, headers
        
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return None, {}
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title."""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract meta description."""
        meta_tag = soup.find("meta", {"name": "description"})
        if meta_tag and meta_tag.get("content"):
            return meta_tag.get("content").strip()
        
        return None
    
    def _detect_tech_stack(self, html_content: str, headers: Dict) -> List[str]:
        """Detect technologies used."""
        detected = set()
        
        # Check HTML content
        for tech, patterns in self.TECH_SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    detected.add(tech)
                    break
        
        # Check response headers
        server = headers.get("Server", "").lower()
        if "nginx" in server:
            detected.add("Nginx")
        if "apache" in server:
            detected.add("Apache")
        
        x_powered_by = headers.get("X-Powered-By", "").lower()
        if x_powered_by:
            if "php" in x_powered_by:
                detected.add("PHP")
            if "asp" in x_powered_by:
                detected.add("ASP.NET")
            if "express" in x_powered_by:
                detected.add("Express")
        
        return sorted(list(detected))
    
    def _extract_emails(self, html_content: str) -> List[str]:
        """Extract email addresses."""
        emails = set()
        
        # Find mailto links
        mailto_matches = re.findall(r"mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", html_content)
        emails.update(mailto_matches)
        
        # Find email patterns in text
        email_matches = re.findall(self.EMAIL_PATTERN, html_content)
        emails.update(email_matches)
        
        # Filter out common non-contact emails
        filtered = [
            e for e in emails
            if not any(x in e.lower() for x in ["noreply", "no-reply", "do-not-reply"])
        ]
        
        return sorted(list(set(filtered)))[:10]  # Limit to 10
    
    def _extract_social_links(self, html_content: str) -> Dict[str, str]:
        """Extract social media links."""
        social_links = {}
        
        for platform, pattern in self.SOCIAL_PATTERNS.items():
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                # Take first unique match
                match = matches[0]
                if isinstance(match, tuple):
                    match = match[0] + match[1] + match[2]
                
                if not match.startswith("http"):
                    match = "https://" + match
                
                social_links[platform] = match
        
        return social_links
    
    def _extract_scripts(self, soup: BeautifulSoup) -> List[str]:
        """Extract external script sources."""
        scripts = set()
        
        for script_tag in soup.find_all("script"):
            src = script_tag.get("src")
            if src:
                # Extract meaningful script names
                if any(x in src.lower() for x in ["analytics", "gtag", "facebook", "twitter"]):
                    scripts.add(src.split("?")[0])  # Remove query params
        
        return sorted(list(scripts))[:15]  # Limit to 15
    
    def _analyze_performance(self, soup: BeautifulSoup, html: str, headers: Dict) -> List[str]:
        """Analyze performance hints."""
        hints = []
        
        # Check for lazy loading
        if "loading" in html:
            hints.append("✓ Lazy loading implemented")
        else:
            hints.append("⚠ Consider implementing lazy loading for images")
        
        # Check for compression
        content_encoding = headers.get("Content-Encoding", "").lower()
        if "gzip" in content_encoding or "brotli" in content_encoding:
            hints.append("✓ Response compression enabled")
        else:
            hints.append("⚠ Enable response compression (gzip/brotli)")
        
        # Check for caching
        cache_control = headers.get("Cache-Control", "").lower()
        if cache_control:
            hints.append("✓ Cache headers configured")
        else:
            hints.append("⚠ Configure Cache-Control headers")
        
        # Check for CDN
        if any(x in headers.get("Server", "").lower() for x in ["cloudflare", "akamai", "cloudfront"]):
            hints.append("✓ Using CDN")
        
        # Check for HTTP/2
        if headers.get("Server") and "http/2" in str(headers):
            hints.append("✓ HTTP/2 enabled")
        
        # Check images
        img_count = len(soup.find_all("img"))
        if img_count > 20:
            hints.append(f"⚠ High number of images ({img_count})")
        
        # Check CSS/JS files
        css_count = len(soup.find_all("link", {"rel": "stylesheet"}))
        if css_count > 5:
            hints.append(f"⚠ Multiple CSS files ({css_count}) - consider consolidation")
        
        return hints[:8]  # Limit to 8 hints
    
    def _generate_ai_summary(
        self,
        title: str,
        description: str,
        tech_stack: List[str],
        performance_hints: List[str]
    ) -> str:
        """
        Generate AI-like summary of website.
        Uses heuristics and detected data.
        """
        parts = []
        
        # Tech stack analysis
        if tech_stack:
            tech_desc = self._describe_tech_stack(tech_stack)
            parts.append(f"This is a modern web application built with {tech_desc}.")
        
        # Purpose analysis
        if title:
            if any(x in title.lower() for x in ["shop", "store", "ecommerce"]):
                parts.append("It appears to be an e-commerce platform.")
            elif any(x in title.lower() for x in ["blog", "news", "media"]):
                parts.append("This is a content/publishing platform.")
            elif any(x in title.lower() for x in ["app", "software", "saas"]):
                parts.append("It's a software-as-a-service application.")
        
        # Performance assessment
        performance_score = len([h for h in performance_hints if h.startswith("✓")])
        total_checks = len(performance_hints)
        
        if performance_score >= 6:
            parts.append("The site demonstrates strong performance optimization practices.")
        elif performance_score >= 3:
            parts.append("Performance optimization opportunities exist.")
        else:
            parts.append("Performance improvements are recommended.")
        
        if not parts:
            return "A modern web application with standard web technologies."
        
        summary = " ".join(parts)
        # Ensure it ends with period
        if not summary.endswith("."):
            summary += "."
        
        return summary
    
    @staticmethod
    def _describe_tech_stack(tech_stack: List[str]) -> str:
        """Describe tech stack in human-readable form."""
        if not tech_stack:
            return "standard web technologies"
        
        # Categorize stack
        frontend = [t for t in tech_stack if t in ["React", "Vue", "Angular", "Svelte", "Next.js", "Nuxt"]]
        backend = [t for t in tech_stack if t in ["Node.js", "Python/Django", "Flask", "FastAPI", "PHP", "ASP.NET"]]
        frameworks = [t for t in tech_stack if t in ["Bootstrap", "Tailwind", "Angular"]]
        
        parts = []
        
        if frontend:
            parts.append(f"frontend framework ({', '.join(frontend)})")
        
        if backend:
            parts.append(f"backend ({', '.join(backend)})")
        
        if frameworks and not frontend:
            parts.append(f"framework ({', '.join(frameworks)})")
        
        if not parts:
            parts.append(", ".join(tech_stack[:3]))
        
        return " and ".join(parts)
    
    @staticmethod
    def _error_response(url: str, error: str) -> Dict:
        """Generate error response."""
        return {
            "url": url,
            "status": "error",
            "error": error,
            "title": None,
            "description": None,
            "tech_stack": [],
            "emails": [],
            "social_links": {},
            "scripts": [],
            "performance_hints": [],
            "ai_summary": "Unable to analyze website.",
            "analyzed_at": datetime.utcnow().isoformat()
        }
