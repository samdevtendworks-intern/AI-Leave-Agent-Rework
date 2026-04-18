"""
Rules Engine
Implements business logic for leave approval recommendations
"""
from typing import List, Optional
from app.models import (
    RecommendationType, Factor, FactorType, 
    LeaveRequest, EmployeeHistory
)
from app.config import settings


class RulesEngine:
    """
    Implements business rules for leave recommendations
    
    Rules Priority:
    1. Burnout Detection (Force Approve)
    2. Capacity Constraints (Suggest Rejection)
    3. Policy Violations (Suggest Rejection)
    4. Behavioral Concerns (Review Required)
    5. Normal Flow (Approve)
    """
    
    @staticmethod
    def determine_recommendation(
        availability_pct: float,
        days_until: int,
        factors: List[Factor],
        history: Optional[EmployeeHistory] = None,
        sentiment: Optional[dict] = None
    ) -> RecommendationType:
        """
        Determine the final recommendation based on all factors
        
        Args:
            availability_pct: Team availability percentage
            days_until: Days until leave starts
            factors: List of contributing factors
            history: Employee history (optional)
            sentiment: Sentiment/urgency analysis of leave reason (optional)
        
        Returns:
            Recommendation type
        """
        # RULE 1: Burnout Detection - STRONGLY APPROVE
        if RulesEngine._check_burnout_risk(factors):
            return RecommendationType.STRONGLY_APPROVE
        
        # RULE 2: Critical Capacity - SUGGEST REJECTION
        if availability_pct < 50:
            return RecommendationType.SUGGEST_REJECTION
        
        # RULE 3: High capacity risk + short notice - SUGGEST REJECTION
        if availability_pct < 60 and days_until < 3:
            return RecommendationType.SUGGEST_REJECTION
        
        # RULE 4: Moderate capacity risk (50-80%) - REVIEW REQUIRED
        if availability_pct < settings.min_team_capacity_percentage:
            # If it's a high priority/emergency, we might still approve but note the risk
            if sentiment and sentiment.get("priority") == "high":
                return RecommendationType.APPROVE
            return RecommendationType.REVIEW_REQUIRED
        
        # RULE 5: Short notice - REVIEW REQUIRED
        if days_until < 7:
            # Urgent medical/emergency might override short notice for recommendation
            if sentiment and sentiment.get("category") == "urgent":
                return RecommendationType.APPROVE
            return RecommendationType.REVIEW_REQUIRED
        
        # RULE 6: Multiple behavioral flags - REVIEW REQUIRED
        behavioral_factors = [
            f for f in factors 
            if f.type in [FactorType.BEHAVIOR, FactorType.WEEKEND_EXTENSION]
        ]
        if len(behavioral_factors) >= 2:
            return RecommendationType.REVIEW_REQUIRED
        
        # RULE 7: Good availability + sufficient notice - APPROVE
        if availability_pct >= 80 and days_until >= 7:
            return RecommendationType.APPROVE
        
        # RULE 8: Default to APPROVE if no major issues
        return RecommendationType.APPROVE
    
    @staticmethod
    def _check_burnout_risk(factors: List[Factor]) -> bool:
        """Check if any factor indicates burnout risk"""
        return any(f.type == FactorType.BURNOUT_RISK for f in factors)
    
    @staticmethod
    def calculate_confidence(
        recommendation: RecommendationType,
        availability_pct: float,
        factors: List[Factor]
    ) -> float:
        """
        Calculate confidence score for the recommendation
        
        Args:
            recommendation: The recommendation type
            availability_pct: Team availability percentage
            factors: List of factors
        
        Returns:
            Confidence score between 0 and 1
        """
        base_confidence = {
            RecommendationType.STRONGLY_APPROVE: 0.95,
            RecommendationType.APPROVE: 0.85,
            RecommendationType.REVIEW_REQUIRED: 0.75,
            RecommendationType.SUGGEST_REJECTION: 0.90
        }
        
        confidence = base_confidence.get(recommendation, 0.80)
        
        # Adjust based on availability clarity
        if availability_pct > 90 or availability_pct < 40:
            # Very clear cases
            confidence = min(confidence + 0.05, 1.0)
        elif 60 <= availability_pct <= 75:
            # Ambiguous cases
            confidence = max(confidence - 0.10, 0.60)
        
        # Adjust based on number of factors
        if len(factors) == 0:
            confidence = max(confidence - 0.05, 0.70)
        elif len(factors) >= 3:
            confidence = min(confidence + 0.05, 0.95)
        
        return round(confidence, 2)
    
    @staticmethod
    def prioritize_factors(factors: List[Factor]) -> List[Factor]:
        """
        Sort factors by priority/severity
        
        Args:
            factors: List of factors
        
        Returns:
            Sorted list with most important factors first
        """
        # Define priority order
        priority_order = {
            FactorType.BURNOUT_RISK: 1,
            FactorType.PRIORITY: 2,
            FactorType.CAPACITY_RISK: 3,
            FactorType.POLICY_VIOLATION: 4,
            FactorType.SHORT_NOTICE: 5,
            FactorType.BEHAVIOR: 6,
            FactorType.WEEKEND_EXTENSION: 7
        }
        
        def sort_key(factor: Factor):
            priority = priority_order.get(factor.type, 99)
            severity = factor.severity or 0.5
            return (priority, -severity)  # Lower priority number = higher importance
        
        return sorted(factors, key=sort_key)
    
    @staticmethod
    def generate_quick_summary(
        recommendation: RecommendationType,
        availability_pct: float,
        overlapping_count: int
    ) -> str:
        """
        Generate a quick text summary without AI
        
        Args:
            recommendation: Recommendation type
            availability_pct: Team availability
            overlapping_count: Number of overlapping members
        
        Returns:
            Summary string
        """
        if recommendation == RecommendationType.STRONGLY_APPROVE:
            return "Employee is at risk of burnout. Strongly recommend approval to maintain wellbeing."
        
        elif recommendation == RecommendationType.SUGGEST_REJECTION:
            return f"Team capacity critically low ({availability_pct}%). Consider rejecting or requesting shorter duration."
        
        elif recommendation == RecommendationType.REVIEW_REQUIRED:
            total_absent = overlapping_count + 1
            return f"Team availability at {availability_pct}% ({total_absent} members absent including applicant). Manual review recommended."
        
        else:  # APPROVE
            return f"Team has sufficient capacity ({availability_pct}% available). Recommend approval."
