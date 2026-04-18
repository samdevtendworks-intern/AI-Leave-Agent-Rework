"""
Test Suite for Rules Engine
Tests business logic and decision-making rules
"""
import pytest
from app.rules_engine import RulesEngine
from app.models import (
    RecommendationType, Factor, FactorType,
    EmployeeHistory
)
from datetime import date


class TestRecommendationLogic:
    """Test recommendation determination logic"""
    
    def test_burnout_forces_strong_approval(self):
        """Burnout detection should force STRONGLY_APPROVE"""
        factors = [
            Factor(
                type=FactorType.BURNOUT_RISK,
                message="Employee hasn't taken leave in 8 months",
                severity=0.9
            )
        ]
        
        recommendation = RulesEngine.determine_recommendation(
            availability_pct=50.0,
            days_until=10,
            factors=factors
        )
        
        assert recommendation == RecommendationType.STRONGLY_APPROVE
    
    def test_critical_capacity_suggests_rejection(self):
        """Critical capacity should suggest rejection"""
        factors = [
            Factor(
                type=FactorType.CAPACITY_RISK,
                message="Critical capacity",
                severity=1.0
            )
        ]
        
        recommendation = RulesEngine.determine_recommendation(
            availability_pct=40.0,
            days_until=10,
            factors=factors
        )
        
        assert recommendation == RecommendationType.SUGGEST_REJECTION
    
    def test_moderate_capacity_requires_review(self):
        """Moderate capacity should require review"""
        factors = [
            Factor(
                type=FactorType.CAPACITY_RISK,
                message="Moderate capacity risk",
                severity=0.7
            )
        ]
        
        recommendation = RulesEngine.determine_recommendation(
            availability_pct=65.0,
            days_until=10,
            factors=factors
        )
        
        assert recommendation == RecommendationType.REVIEW_REQUIRED
    
    def test_good_capacity_approves(self):
        """Good capacity with sufficient notice should approve"""
        factors = []
        
        recommendation = RulesEngine.determine_recommendation(
            availability_pct=85.0,
            days_until=10,
            factors=factors
        )
        
        assert recommendation == RecommendationType.APPROVE
    
    def test_short_notice_with_concerns(self):
        """Short notice with behavioral concerns requires review"""
        factors = [
            Factor(
                type=FactorType.BEHAVIOR,
                message="Frequent weekend extensions",
                severity=0.4
            ),
            Factor(
                type=FactorType.SHORT_NOTICE,
                message="Only 2 days notice",
                severity=0.8
            )
        ]
        
        recommendation = RulesEngine.determine_recommendation(
            availability_pct=75.0,
            days_until=2,
            factors=factors
        )
        
        assert recommendation == RecommendationType.REVIEW_REQUIRED


class TestConfidenceScore:
    """Test confidence score calculation"""
    
    def test_high_confidence_for_clear_cases(self):
        """Very high or very low capacity should have high confidence"""
        # High capacity
        confidence = RulesEngine.calculate_confidence(
            recommendation=RecommendationType.APPROVE,
            availability_pct=95.0,
            factors=[]
        )
        assert confidence >= 0.85
        
        # Low capacity
        confidence = RulesEngine.calculate_confidence(
            recommendation=RecommendationType.SUGGEST_REJECTION,
            availability_pct=30.0,
            factors=[Factor(type=FactorType.CAPACITY_RISK, message="Low", severity=1.0)]
        )
        assert confidence >= 0.90
    
    def test_lower_confidence_for_ambiguous_cases(self):
        """Ambiguous capacity should have lower confidence"""
        confidence = RulesEngine.calculate_confidence(
            recommendation=RecommendationType.REVIEW_REQUIRED,
            availability_pct=68.0,
            factors=[]
        )
        assert confidence <= 0.75
    
    def test_multiple_factors_increase_confidence(self):
        """Multiple supporting factors should increase confidence"""
        many_factors = [
            Factor(type=FactorType.CAPACITY_RISK, message="Risk", severity=0.7),
            Factor(type=FactorType.BEHAVIOR, message="Pattern", severity=0.5),
            Factor(type=FactorType.SHORT_NOTICE, message="Notice", severity=0.6)
        ]
        
        confidence_many = RulesEngine.calculate_confidence(
            recommendation=RecommendationType.REVIEW_REQUIRED,
            availability_pct=65.0,
            factors=many_factors
        )
        
        confidence_few = RulesEngine.calculate_confidence(
            recommendation=RecommendationType.REVIEW_REQUIRED,
            availability_pct=65.0,
            factors=many_factors[:1]
        )
        
        # More factors should give higher confidence
        assert confidence_many >= confidence_few


class TestFactorPrioritization:
    """Test factor sorting by priority"""
    
    def test_burnout_highest_priority(self):
        """Burnout factors should be prioritized first"""
        factors = [
            Factor(type=FactorType.WEEKEND_EXTENSION, message="Weekend", severity=0.3),
            Factor(type=FactorType.BURNOUT_RISK, message="Burnout", severity=0.9),
            Factor(type=FactorType.CAPACITY_RISK, message="Capacity", severity=0.7)
        ]
        
        sorted_factors = RulesEngine.prioritize_factors(factors)
        
        assert sorted_factors[0].type == FactorType.BURNOUT_RISK
    
    def test_capacity_before_behavior(self):
        """Capacity risks should come before behavioral factors"""
        factors = [
            Factor(type=FactorType.BEHAVIOR, message="Behavior", severity=0.6),
            Factor(type=FactorType.CAPACITY_RISK, message="Capacity", severity=0.7)
        ]
        
        sorted_factors = RulesEngine.prioritize_factors(factors)
        
        assert sorted_factors[0].type == FactorType.CAPACITY_RISK
        assert sorted_factors[1].type == FactorType.BEHAVIOR
    
    def test_severity_within_same_type(self):
        """Higher severity should come first within same type"""
        factors = [
            Factor(type=FactorType.BEHAVIOR, message="Low", severity=0.3),
            Factor(type=FactorType.BEHAVIOR, message="High", severity=0.8)
        ]
        
        sorted_factors = RulesEngine.prioritize_factors(factors)
        
        assert sorted_factors[0].severity > sorted_factors[1].severity


class TestQuickSummary:
    """Test quick summary generation"""
    
    def test_strongly_approve_summary(self):
        """Test summary for strong approval"""
        summary = RulesEngine.generate_quick_summary(
            recommendation=RecommendationType.STRONGLY_APPROVE,
            availability_pct=70.0,
            overlapping_count=1
        )
        
        assert "burnout" in summary.lower()
        assert "approv" in summary.lower()
    
    def test_suggest_rejection_summary(self):
        """Test summary for suggested rejection"""
        summary = RulesEngine.generate_quick_summary(
            recommendation=RecommendationType.SUGGEST_REJECTION,
            availability_pct=35.0,
            overlapping_count=3
        )
        
        assert "35" in summary
        assert "reject" in summary.lower() or "shorter" in summary.lower()
    
    def test_review_required_summary(self):
        """Test summary for review required"""
        summary = RulesEngine.generate_quick_summary(
            recommendation=RecommendationType.REVIEW_REQUIRED,
            availability_pct=65.0,
            overlapping_count=2
        )
        
        assert "65" in summary
        assert "review" in summary.lower()
    
    def test_approve_summary(self):
        """Test summary for approval"""
        summary = RulesEngine.generate_quick_summary(
            recommendation=RecommendationType.APPROVE,
            availability_pct=85.0,
            overlapping_count=1
        )
        
        assert "85" in summary
        assert "approv" in summary.lower()
        assert "sufficient" in summary.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
