"""
Compensation Market Data Service
Integrates with salary data APIs for market benchmarking.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class SalaryDataPoint:
    """Single salary data point from market sources."""
    title: str
    location: str
    min_salary: float
    max_salary: float
    median_salary: float
    percentile_25: float
    percentile_75: float
    currency: str
    source: str
    sample_size: int
    date_collected: datetime

@dataclass
class MarketBenchmark:
    """Market benchmark for a role."""
    role: str
    location: str
    market_median: float
    market_p25: float
    market_p75: float
    internal_median: Optional[float] = None
    variance_pct: Optional[float] = None
    data_points: int = 0
    sources: List[str] = None

class CompensationMarketService:
    """Service for fetching and analyzing compensation market data."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # API configurations (would be set via env vars in production)
        self.levels_fyi_api = os.getenv("LEVELS_FYI_API", "https://www.levels.fyi/api")
        self.glassdoor_api = os.getenv("GLASSDOOR_API", "")
        self.payscale_api = os.getenv("PAYSCALE_API", "")
        
        # Mock data for development
        self.mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict[str, List[SalaryDataPoint]]:
        """Load mock salary data for development."""
        from datetime import datetime, timedelta
        
        base_date = datetime.utcnow() - timedelta(days=30)
        
        return {
            "Software Engineer": [
                SalaryDataPoint(
                    title="Software Engineer",
                    location="San Francisco, CA",
                    min_salary=120000,
                    max_salary=200000,
                    median_salary=165000,
                    percentile_25=140000,
                    percentile_75=190000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=1250,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Software Engineer",
                    location="New York, NY",
                    min_salary=115000,
                    max_salary=185000,
                    median_salary=155000,
                    percentile_25=130000,
                    percentile_75=175000,
                    currency="USD",
                    source="glassdoor",
                    sample_size=890,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Software Engineer",
                    location="Seattle, WA",
                    min_salary=110000,
                    max_salary=180000,
                    median_salary=150000,
                    percentile_25=128000,
                    percentile_75=170000,
                    currency="USD",
                    source="payscale",
                    sample_size=650,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Software Engineer",
                    location="Austin, TX",
                    min_salary=95000,
                    max_salary=160000,
                    median_salary=130000,
                    percentile_25=110000,
                    percentile_75=150000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=420,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Software Engineer",
                    location="Remote",
                    min_salary=90000,
                    max_salary=170000,
                    median_salary=135000,
                    percentile_25=115000,
                    percentile_75=155000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=2100,
                    date_collected=base_date
                ),
            ],
            "Senior Software Engineer": [
                SalaryDataPoint(
                    title="Senior Software Engineer",
                    location="San Francisco, CA",
                    min_salary=160000,
                    max_salary=280000,
                    median_salary=220000,
                    percentile_25=185000,
                    percentile_75=250000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=890,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Senior Software Engineer",
                    location="New York, NY",
                    min_salary=155000,
                    max_salary=260000,
                    median_salary=205000,
                    percentile_25=175000,
                    percentile_75=235000,
                    currency="USD",
                    source="glassdoor",
                    sample_size=560,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Senior Software Engineer",
                    location="Remote",
                    min_salary=140000,
                    max_salary=240000,
                    median_salary=190000,
                    percentile_25=160000,
                    percentile_75=220000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=1800,
                    date_collected=base_date
                ),
            ],
            "Product Manager": [
                SalaryDataPoint(
                    title="Product Manager",
                    location="San Francisco, CA",
                    min_salary=140000,
                    max_salary=220000,
                    median_salary=180000,
                    percentile_25=155000,
                    percentile_75=205000,
                    currency="USD",
                    source="glassdoor",
                    sample_size=420,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Product Manager",
                    location="New York, NY",
                    min_salary=135000,
                    max_salary=210000,
                    median_salary=172000,
                    percentile_25=150000,
                    percentile_75=195000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=310,
                    date_collected=base_date
                ),
            ],
            "Data Scientist": [
                SalaryDataPoint(
                    title="Data Scientist",
                    location="San Francisco, CA",
                    min_salary=130000,
                    max_salary=210000,
                    median_salary=170000,
                    percentile_25=145000,
                    percentile_75=195000,
                    currency="USD",
                    source="glassdoor",
                    sample_size=380,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Data Scientist",
                    location="Remote",
                    min_salary=110000,
                    max_salary=185000,
                    median_salary=145000,
                    percentile_25=125000,
                    percentile_75=165000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=650,
                    date_collected=base_date
                ),
            ],
            "DevOps Engineer": [
                SalaryDataPoint(
                    title="DevOps Engineer",
                    location="San Francisco, CA",
                    min_salary=135000,
                    max_salary=215000,
                    median_salary=175000,
                    percentile_25=150000,
                    percentile_75=200000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=280,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="DevOps Engineer",
                    location="Remote",
                    min_salary=115000,
                    max_salary=180000,
                    median_salary=145000,
                    percentile_25=125000,
                    percentile_75=165000,
                    currency="USD",
                    source="glassdoor",
                    sample_size=190,
                    date_collected=base_date
                ),
            ],
            "Engineering Manager": [
                SalaryDataPoint(
                    title="Engineering Manager",
                    location="San Francisco, CA",
                    min_salary=190000,
                    max_salary=320000,
                    median_salary=255000,
                    percentile_25=215000,
                    percentile_75=290000,
                    currency="USD",
                    source="levels.fyi",
                    sample_size=180,
                    date_collected=base_date
                ),
                SalaryDataPoint(
                    title="Engineering Manager",
                    location="Remote",
                    min_salary=170000,
                    max_salary=280000,
                    median_salary=225000,
                    percentile_25=190000,
                    percentile_75=255000,
                    currency="USD",
                    source="glassdoor",
                    sample_size=120,
                    date_collected=base_date
                ),
            ],
        }
    
    async def get_market_data(
        self,
        role: str,
        location: str = "Remote",
        experience_level: str = "mid"
    ) -> List[SalaryDataPoint]:
        """
        Get market salary data for a role and location.
        
        Args:
            role: Job title
            location: Geographic location
            experience_level: junior, mid, senior, lead, manager
            
        Returns:
            List of salary data points
        """
        cache_key = f"{role}:{location}:{experience_level}"
        
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if (datetime.utcnow() - cached["timestamp"]).seconds < self.cache_ttl:
                return cached["data"]
        
        # Try to fetch from APIs
        data = await self._fetch_from_apis(role, location, experience_level)
        
        if not data:
            # Fallback to mock data
            data = self._get_mock_data(role, location)
        
        # Cache results
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
        return data
    
    async def _fetch_from_apis(
        self,
        role: str,
        location: str,
        experience_level: str
    ) -> List[SalaryDataPoint]:
        """Fetch salary data from external APIs."""
        data = []
        
        # In production, implement actual API calls:
        # - levels.fyi API
        # - Glassdoor API
        # - PayScale API
        # - LinkedIn Salary API
        # - Bureau of Labor Statistics (BLS) API
        
        # For now, return empty to use mock data
        return data
    
    def _get_mock_data(self, role: str, location: str) -> List[SalaryDataPoint]:
        """Get mock data for role/location."""
        # Normalize role
        role_map = {
            "software engineer": "Software Engineer",
            "senior software engineer": "Senior Software Engineer",
            "product manager": "Product Manager",
            "data scientist": "Data Scientist",
            "devops engineer": "DevOps Engineer",
            "engineering manager": "Engineering Manager",
        }
        
        normalized_role = role_map.get(role.lower(), role)
        role_data = self.mock_data.get(normalized_role, [])
        
        # Filter by location (fuzzy match)
        location_lower = location.lower()
        filtered = [
            d for d in role_data
            if location_lower in d.location.lower() or 
               location_lower == "remote" or
               d.location.lower() == "remote"
        ]
        
        return filtered if filtered else role_data[:3]  # Return top 3 if no location match
    
    def calculate_benchmark(
        self,
        role: str,
        location: str,
        internal_salaries: List[float]
    ) -> MarketBenchmark:
        """
        Calculate market benchmark against internal salaries.
        
        Args:
            role: Job title
            location: Geographic location
            internal_salaries: List of internal employee salaries
            
        Returns:
            MarketBenchmark with comparison metrics
        """
        market_data = self._get_mock_data(role, location)
        
        if not market_data:
            return MarketBenchmark(
                role=role,
                location=location,
                market_median=0,
                market_p25=0,
                market_p75=0,
                data_points=0
            )
        
        # Calculate market statistics
        salaries = [d.median_salary for d in market_data]
        salaries.sort()
        
        market_median = salaries[len(salaries) // 2]
        market_p25 = salaries[len(salaries) // 4]
        market_p75 = salaries[3 * len(salaries) // 4]
        
        internal_median = None
        variance_pct = None
        
        if internal_salaries:
            internal_salaries.sort()
            internal_median = internal_salaries[len(internal_salaries) // 2]
            
            if market_median > 0:
                variance_pct = ((internal_median - market_median) / market_median) * 100
        
        return MarketBenchmark(
            role=role,
            location=location,
            market_median=market_median,
            market_p25=market_p25,
            market_p75=market_p75,
            internal_median=internal_median,
            variance_pct=variance_pct,
            data_points=len(market_data),
            sources=list(set(d.source for d in market_data))
        )
    
    def analyze_pay_equity(
        self,
        compensation_data: List[Dict[str, Any]],
        market_benchmarks: Dict[str, MarketBenchmark]
    ) -> Dict[str, Any]:
        """
        Analyze pay equity across demographics and market benchmarks.
        
        Args:
            compensation_data: List of employee compensation records
            market_benchmarks: Pre-calculated market benchmarks by role
            
        Returns:
            Analysis results with equity metrics
        """
        from collections import defaultdict
        import numpy as np
        
        if not compensation_data:
            return {"error": "No compensation data provided"}
        
        # Group by role
        by_role = defaultdict(list)
        for record in compensation_data:
            role = record.get("role", "Unknown")
            by_role[role].append(record)
        
        results = {
            "overall": {},
            "by_role": {},
            "by_demographic": {},
            "market_comparison": {},
            "recommendations": []
        }
        
        # Overall statistics
        all_salaries = [r.get("salary", 0) for r in compensation_data if r.get("salary")]
        if all_salaries:
            results["overall"] = {
                "count": len(all_salaries),
                "mean": np.mean(all_salaries),
                "median": np.median(all_salaries),
                "std": np.std(all_salaries),
                "min": np.min(all_salaries),
                "max": np.max(all_salaries)
            }
        
        # By role analysis
        for role, records in by_role.items():
            role_salaries = [r.get("salary", 0) for r in records if r.get("salary")]
            if not role_salaries:
                continue
            
            market = market_benchmarks.get(role)
            
            role_analysis = {
                "count": len(role_salaries),
                "mean": np.mean(role_salaries),
                "median": np.median(role_salaries),
                "std": np.std(role_salaries),
                "min": np.min(role_salaries),
                "max": np.max(role_salaries)
            }
            
            if market:
                role_analysis["market_median"] = market.market_median
                role_analysis["market_p25"] = market.market_p25
                role_analysis["market_p75"] = market.market_p75
                
                if market.median_median > 0:
                    variance = ((role_analysis["median"] - market.median_median) / market.median_median) * 100
                    role_analysis["market_variance_pct"] = round(variance, 1)
                    
                    if variance < -15:
                        role_analysis["status"] = "below_market"
                        results["recommendations"].append(
                            f"{role}: Median salary {abs(variance):.0f}% below market. Consider adjustment."
                        )
                    elif variance > 15:
                        role_analysis["status"] = "above_market"
                    else:
                        role_analysis["status"] = "competitive"
            
            results["by_role"][role] = role_analysis
        
        # Demographic analysis (if available)
        demographic_fields = ["gender", "ethnicity", "age_group", "department"]
        for field in demographic_fields:
            by_demo = defaultdict(list)
            for record in compensation_data:
                demo = record.get(field)
                if demo and record.get("salary"):
                    by_demo[demo].append(record["salary"])
            
            if by_demo:
                demo_analysis = {}
                for demo, salaries in by_demo.items():
                    demo_analysis[demo] = {
                        "count": len(salaries),
                        "median": np.median(salaries),
                        "mean": np.mean(salaries)
                    }
                results["by_demographic"][field] = demo_analysis
        
        # Market comparison summary
        below_market = sum(
            1 for r in results["by_role"].values()
            if r.get("status") == "below_market"
        )
        above_market = sum(
            1 for r in results["by_role"].values()
            if r.get("status") == "above_market"
        )
        
        results["market_comparison"] = {
            "roles_below_market": below_market,
            "roles_above_market": above_market,
            "roles_competitive": len(results["by_role"]) - below_market - above_market,
            "total_roles_analyzed": len(results["by_role"])
        }
        
        return results


# Global instance
compensation_market_service = CompensationMarketService()