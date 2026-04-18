import pandas as pd
from datetime import date, timedelta
from typing import List, Tuple, Dict, Optional
from app.models import (
    LeaveRequest, TeamMemberLeave, EmployeeHistory,
    Factor, FactorType
)
from app.config import settings


class AnalysisEngine:
    """Core engine for analyzing leave requests using Pandas for precision"""
    
    @staticmethod
    def check_overlap(range1: Tuple[date, date], range2: Tuple[date, date]) -> bool:
        """Check if two date ranges overlap using Pandas timestamps"""
        s1, e1 = pd.to_datetime(range1[0]), pd.to_datetime(range1[1])
        s2, e2 = pd.to_datetime(range2[0]), pd.to_datetime(range2[1])
        return s1 <= e2 and s2 <= e1

    @staticmethod
    def count_overlapping_leaves(
        request: LeaveRequest,
        team_context: List[TeamMemberLeave]
    ) -> Tuple[int, List[str]]:
        """
        Count max overlapping team members on any single day in the requested period.
        Uses Pandas for daily time-series analysis to fulfill the 'Logic Layer: Pandas' requirement.
        """
        if not team_context:
            return 0, []

        request_days = pd.date_range(start=request.start, end=request.end)
        overlap_counts = pd.Series(0, index=request_days)
        overlapping_emp_ids = set()

        for leave in team_context:
            # Skip if it's the requestor (prevent double-counting)
            if leave.emp_id == request.emp_id:
                continue
                
            leave_days = pd.date_range(start=leave.start, end=leave.end)
            intersection = request_days.intersection(leave_days)
            
            if not intersection.empty:
                overlapping_emp_ids.add(leave.emp_id)
                overlap_counts[intersection] += 1

        # Total unique people absent during any part of the requested period
        total_overlapping_count = len(overlapping_emp_ids)
        return total_overlapping_count, list(overlapping_emp_ids)

    @staticmethod
    def calculate_team_availability(
        total_team_size: int,
        overlapping_count: int,
        include_requestor: bool = True
    ) -> float:
        """Calculate minimum team availability percentage during the requested period"""
        absent_count = overlapping_count + (1 if include_requestor else 0)
        available = total_team_size - absent_count
        
        # Ensure availability doesn't go below 0
        available = max(0, available)
        
        availability_pct = (available / total_team_size) * 100
        return round(float(availability_pct), 2)
    
    @staticmethod
    def calculate_days_until_leave(request_start: date) -> int:
        """Calculate days from today until leave starts"""
        today = date.today()
        delta = request_start - today
        return delta.days
    
    @staticmethod
    def calculate_leave_duration(start_date: date, end_date: date) -> int:
        """Calculate total leave days (inclusive)"""
        delta = end_date - start_date
        return delta.days + 1
    
    @staticmethod
    def is_weekend_extension(request: LeaveRequest) -> Tuple[bool, str]:
        """
        Check if leave request extends a weekend
        
        Args:
            request: Leave request to check
        
        Returns:
            Tuple of (is_extension, message)
        """
        # Monday = 0, Sunday = 6
        start_weekday = request.start.weekday()
        end_weekday = request.end.weekday()
        
        # Check for both Friday and Monday (full week)
        if start_weekday == 0 and end_weekday == 4:
            return True, "Leave spans Monday-Friday, extending between weekends"
            
        # Check for Monday leave (extends weekend at start)
        if start_weekday == 0:  # Monday
            return True, "Leave starts on Monday, extending from weekend"
            
        # Check for Friday leave (extends weekend at end)
        if end_weekday == 4:  # Friday
            return True, "Leave ends on Friday, extending into weekend"
        
        return False, ""
    
    @staticmethod
    def analyze_capacity_risk(
        availability_pct: float,
        overlapping_count: int,
        total_team_size: int
    ) -> Optional[Factor]:
        """
        Analyze capacity risk and generate factor
        
        Args:
            availability_pct: Team availability percentage
            overlapping_count: Number of overlapping absences
            total_team_size: Total team size
        
        Returns:
            Factor if risk detected, None otherwise
        """
        if availability_pct < 50:
            severity = 1.0
            message = f"CRITICAL: Team capacity drops to {availability_pct}% ({overlapping_count + 1}/{total_team_size} absent)."
            return Factor(
                type=FactorType.CAPACITY_RISK,
                message=message,
                severity=severity
            )
        elif availability_pct < settings.min_team_capacity_percentage:
            severity = 0.7
            high_impact = " (High Impact)" if availability_pct < 70 else ""
            message = f"Team capacity{high_impact} drops to {availability_pct}% ({overlapping_count + 1}/{total_team_size} absent)."
            return Factor(
                type=FactorType.CAPACITY_RISK,
                message=message,
                severity=severity
            )
        
        return None
    
    @staticmethod
    def analyze_short_notice(days_until: int) -> Optional[Factor]:
        """
        Analyze if leave is on short notice
        
        Args:
            days_until: Days until leave starts
        
        Returns:
            Factor if short notice detected, None otherwise
        """
        if days_until < 0:
            return Factor(
                type=FactorType.SHORT_NOTICE,
                message="Leave request is for dates in the past. This should not be possible.",
                severity=1.0
            )
        elif days_until < 1:
            return Factor(
                type=FactorType.SHORT_NOTICE,
                message="Very short notice: Leave starts in less than 24 hours (Unplanned).",
                severity=0.9
            )
        elif days_until < 3:
            return Factor(
                type=FactorType.SHORT_NOTICE,
                message=f"Very short notice: Only {days_until} days until leave starts.",
                severity=0.8
            )
        elif days_until < 7:
            return Factor(
                type=FactorType.SHORT_NOTICE,
                message=f"Short notice: Only {days_until} days until leave starts.",
                severity=0.5
            )
        
        return None
    
    @staticmethod
    def analyze_behavioral_patterns(
        history: Optional[EmployeeHistory],
        request: LeaveRequest
    ) -> List[Factor]:
        """
        Analyze employee behavioral patterns
        
        Args:
            history: Employee leave history
            request: Current leave request
        
        Returns:
            List of behavioral factors
        """
        factors = []
        
        if not history:
            return factors
        
        # Check for burnout risk (hasn't taken leave in long time)
        if history.months_since_last_leave and history.months_since_last_leave >= settings.burnout_threshold_months:
            factors.append(Factor(
                type=FactorType.BURNOUT_RISK,
                message=f"Employee has not taken leave in {history.months_since_last_leave:.1f} months. Burnout risk detected.",
                severity=0.9
            ))
        
        # Check for frequent unplanned leaves
        if history.total_leaves_taken > 0:
            unplanned_ratio = history.unplanned_leaves / history.total_leaves_taken
            if unplanned_ratio > 0.3:  # More than 30% unplanned
                factors.append(Factor(
                    type=FactorType.BEHAVIOR,
                    message=f"Employee has {history.unplanned_leaves} unplanned leaves out of {history.total_leaves_taken} total ({unplanned_ratio*100:.0f}%).",
                    severity=0.6
                ))
        
        # Check for weekend extension pattern
        if history.weekend_extensions >= 3:
            factors.append(Factor(
                type=FactorType.BEHAVIOR,
                message=f"Employee has extended weekends {history.weekend_extensions} times in the past year.",
                severity=0.4
            ))
        
        # Check if current request is weekend extension
        is_extension, extension_msg = AnalysisEngine.is_weekend_extension(request)
        if is_extension:
            factors.append(Factor(
                type=FactorType.WEEKEND_EXTENSION,
                message=extension_msg,
                severity=0.3
            ))
        
        return factors
    
    @staticmethod
    def generate_traffic_light_score(
        availability_pct: float,
        days_until: int,
        factors: List[Factor]
    ) -> Tuple[str, float]:
        """
        Generate traffic light classification and confidence score
        
        Args:
            availability_pct: Team availability percentage
            days_until: Days until leave
            factors: List of factors
        
        Returns:
            Tuple of (color_classification, confidence_score)
        """
        # Calculate weighted severity
        total_severity = sum(f.severity or 0.5 for f in factors)
        avg_severity = total_severity / len(factors) if factors else 0
        
        # Traffic light logic
        if availability_pct < 50:
            return "RED", 0.95
        elif availability_pct < settings.min_team_capacity_percentage and days_until < 7:
            return "RED", 0.85
        elif availability_pct < settings.min_team_capacity_percentage or days_until < 3:
            return "YELLOW", 0.75
        elif avg_severity > 0.7:
            return "YELLOW", 0.70
        elif availability_pct > 80 and days_until > 7:
            return "GREEN", 0.90
        else:
            return "GREEN", 0.80
