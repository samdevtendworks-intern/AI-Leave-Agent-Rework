"""
Test Suite for Analysis Engine
Tests core logic for date overlap, capacity, and behavioral analysis
"""
import pytest
from datetime import date, timedelta
from app.analysis_engine import AnalysisEngine
from app.models import LeaveRequest, TeamMemberLeave, EmployeeHistory, FactorType


class TestDateOverlap:
    """Test date overlap detection"""
    
    def test_no_overlap(self):
        """Test ranges that don't overlap"""
        range1 = (date(2026, 2, 1), date(2026, 2, 5))
        range2 = (date(2026, 2, 10), date(2026, 2, 15))
        assert not AnalysisEngine.check_overlap(range1, range2)
    
    def test_complete_overlap(self):
        """Test ranges that completely overlap"""
        range1 = (date(2026, 2, 1), date(2026, 2, 10))
        range2 = (date(2026, 2, 3), date(2026, 2, 7))
        assert AnalysisEngine.check_overlap(range1, range2)
    
    def test_partial_overlap(self):
        """Test ranges that partially overlap"""
        range1 = (date(2026, 2, 1), date(2026, 2, 10))
        range2 = (date(2026, 2, 5), date(2026, 2, 15))
        assert AnalysisEngine.check_overlap(range1, range2)
    
    def test_single_day_overlap(self):
        """Test ranges that overlap by exactly one day"""
        range1 = (date(2026, 2, 1), date(2026, 2, 5))
        range2 = (date(2026, 2, 5), date(2026, 2, 10))
        assert AnalysisEngine.check_overlap(range1, range2)


class TestCapacityCalculation:
    """Test team capacity calculations"""
    
    def test_full_capacity(self):
        """Test when no one is absent"""
        availability = AnalysisEngine.calculate_team_availability(
            total_team_size=5,
            overlapping_count=0,
            include_requestor=True
        )
        assert availability == 80.0  # 4/5 = 80%
    
    def test_half_capacity(self):
        """Test when half team is absent"""
        availability = AnalysisEngine.calculate_team_availability(
            total_team_size=10,
            overlapping_count=4,
            include_requestor=True
        )
        assert availability == 50.0  # 5/10 = 50%
    
    def test_critical_capacity(self):
        """Test critical low capacity"""
        availability = AnalysisEngine.calculate_team_availability(
            total_team_size=5,
            overlapping_count=3,
            include_requestor=True
        )
        assert availability == 20.0  # 1/5 = 20%


class TestOverlappingLeaves:
    """Test counting overlapping leaves"""
    
    def test_no_overlaps(self):
        """Test when no leaves overlap"""
        request = LeaveRequest(
            emp_id="E001",
            start=date(2026, 3, 1),
            end=date(2026, 3, 5),
            reason="Vacation",
            dept_id="ENG"
        )
        
        team_context = [
            TeamMemberLeave(emp_id="E002", start=date(2026, 2, 1), end=date(2026, 2, 5)),
            TeamMemberLeave(emp_id="E003", start=date(2026, 4, 1), end=date(2026, 4, 5))
        ]
        
        count, ids = AnalysisEngine.count_overlapping_leaves(request, team_context)
        assert count == 0
        assert len(ids) == 0
    
    def test_multiple_overlaps(self):
        """Test when multiple leaves overlap"""
        request = LeaveRequest(
            emp_id="E001",
            start=date(2026, 2, 10),
            end=date(2026, 2, 15),
            reason="Vacation",
            dept_id="ENG"
        )
        
        team_context = [
            TeamMemberLeave(emp_id="E002", start=date(2026, 2, 10), end=date(2026, 2, 12)),
            TeamMemberLeave(emp_id="E003", start=date(2026, 2, 14), end=date(2026, 2, 20)),
            TeamMemberLeave(emp_id="E004", start=date(2026, 3, 1), end=date(2026, 3, 5))
        ]
        
        count, ids = AnalysisEngine.count_overlapping_leaves(request, team_context)
        assert count == 2
        assert "E002" in ids
        assert "E003" in ids
        assert "E004" not in ids


class TestWeekendExtension:
    """Test weekend extension detection"""
    
    def test_monday_extension(self):
        """Test leave starting on Monday"""
        request = LeaveRequest(
            emp_id="E001",
            start=date(2026, 2, 16),  # Monday
            end=date(2026, 2, 17),
            reason="Personal",
            dept_id="ENG"
        )
        
        is_extension, message = AnalysisEngine.is_weekend_extension(request)
        assert is_extension
        assert "Monday" in message
    
    def test_friday_extension(self):
        """Test leave ending on Friday"""
        request = LeaveRequest(
            emp_id="E001",
            start=date(2026, 2, 19),
            end=date(2026, 2, 20),  # Friday
            reason="Personal",
            dept_id="ENG"
        )
        
        is_extension, message = AnalysisEngine.is_weekend_extension(request)
        assert is_extension
        assert "Friday" in message
    
    def test_no_extension(self):
        """Test leave not extending weekend"""
        request = LeaveRequest(
            emp_id="E001",
            start=date(2026, 2, 18),  # Tuesday
            end=date(2026, 2, 19),    # Wednesday
            reason="Personal",
            dept_id="ENG"
        )
        
        is_extension, message = AnalysisEngine.is_weekend_extension(request)
        assert not is_extension


class TestBehavioralAnalysis:
    """Test behavioral pattern analysis"""
    
    def test_burnout_detection(self):
        """Test detection of burnout risk"""
        history = EmployeeHistory(
            emp_id="E001",
            total_leaves_taken=2,
            unplanned_leaves=0,
            weekend_extensions=0,
            last_leave_date=date(2025, 6, 1),
            months_since_last_leave=8.0
        )
        
        request = LeaveRequest(
            emp_id="E001",
            start=date(2026, 2, 20),
            end=date(2026, 2, 21),
            reason="Vacation",
            dept_id="ENG"
        )
        
        factors = AnalysisEngine.analyze_behavioral_patterns(history, request)
        burnout_factors = [f for f in factors if f.type == FactorType.BURNOUT_RISK]
        assert len(burnout_factors) > 0
    
    def test_frequent_unplanned_leaves(self):
        """Test detection of frequent unplanned leaves"""
        history = EmployeeHistory(
            emp_id="E001",
            total_leaves_taken=10,
            unplanned_leaves=5,  # 50% unplanned
            weekend_extensions=1,
            last_leave_date=date(2026, 1, 15),
            months_since_last_leave=1.0
        )
        
        request = LeaveRequest(
            emp_id="E001",
            start=date(2026, 2, 20),
            end=date(2026, 2, 21),
            reason="Sick leave",
            dept_id="ENG"
        )
        
        factors = AnalysisEngine.analyze_behavioral_patterns(history, request)
        behavior_factors = [f for f in factors if f.type == FactorType.BEHAVIOR]
        assert len(behavior_factors) > 0


class TestCapacityRiskAnalysis:
    """Test capacity risk factor generation"""
    
    def test_critical_capacity_risk(self):
        """Test critical capacity generates high severity factor"""
        factor = AnalysisEngine.analyze_capacity_risk(
            availability_pct=40.0,
            overlapping_count=2,
            total_team_size=5
        )
        
        assert factor is not None
        assert factor.type == FactorType.CAPACITY_RISK
        assert factor.severity == 1.0
        assert "CRITICAL" in factor.message
    
    def test_moderate_capacity_risk(self):
        """Test moderate capacity generates medium severity factor"""
        factor = AnalysisEngine.analyze_capacity_risk(
            availability_pct=65.0,
            overlapping_count=1,
            total_team_size=5
        )
        
        assert factor is not None
        assert factor.type == FactorType.CAPACITY_RISK
        assert factor.severity == 0.7
    
    def test_no_capacity_risk(self):
        """Test good capacity generates no factor"""
        factor = AnalysisEngine.analyze_capacity_risk(
            availability_pct=85.0,
            overlapping_count=0,
            total_team_size=5
        )
        
        assert factor is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
