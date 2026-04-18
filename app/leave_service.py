"""
Leave Analysis Service
Main service that orchestrates the complete leave analysis workflow
"""
from typing import List
from app.models import (
    AnalyzeLeaveInput, AnalyzeLeaveOutput,
    RecommendationType, Factor, FactorType, LeaveRequest, TeamMemberLeave
)
from app.analysis_engine import AnalysisEngine
from app.rules_engine import RulesEngine
from app.ai_service import ai_service
from app.data_service import data_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeaveAnalysisService:
    """
    Main service for analyzing leave requests
    
    This service orchestrates:
    1. Capacity analysis
    2. Behavioral pattern detection
    3. Rule-based decision making
    4. AI-powered recommendation generation
    """
    
    def __init__(self):
        """Initialize the leave analysis service"""
        self.analysis_engine = AnalysisEngine()
        self.rules_engine = RulesEngine()
        self.ai_service = ai_service
        self.data_service = data_service
    
    async def analyze_leave_request(
        self,
        input_data: AnalyzeLeaveInput
    ) -> AnalyzeLeaveOutput:
        """
        Perform complete analysis of a leave request
        
        Args:
            input_data: Leave request and team context
        
        Returns:
            Complete analysis with recommendation
        """
        request = input_data.request
        team_context = input_data.team_context
        total_team_size = input_data.total_team_size
        
        logger.info(f"Analyzing leave request for {request.emp_id} from {request.start} to {request.end}")
        
        # STEP 1: Calculate basic metrics
        overlapping_count, overlapping_ids = self.analysis_engine.count_overlapping_leaves(
            request, team_context
        )
        
        availability_pct = self.analysis_engine.calculate_team_availability(
            total_team_size, overlapping_count, include_requestor=True
        )
        
        days_until = self.analysis_engine.calculate_days_until_leave(request.start)
        leave_duration = self.analysis_engine.calculate_leave_duration(request.start, request.end)
        
        logger.info(f"Team availability: {availability_pct}%, Days until: {days_until}, Duration: {leave_duration}")
        
        # STEP 2: Gather all factors
        factors: List[Factor] = []
        
        # Capacity risk factor
        capacity_factor = self.analysis_engine.analyze_capacity_risk(
            availability_pct, overlapping_count, total_team_size
        )
        if capacity_factor:
            factors.append(capacity_factor)
        
        # Short notice factor
        notice_factor = self.analysis_engine.analyze_short_notice(days_until)
        if notice_factor:
            factors.append(notice_factor)
        
        # Behavioral factors
        employee_history = self.data_service.get_employee_history(request.emp_id)
        behavioral_factors = self.analysis_engine.analyze_behavioral_patterns(
            employee_history, request
        )
        factors.extend(behavioral_factors)
        
        # Prioritize factors
        factors = self.rules_engine.prioritize_factors(factors)
        
        logger.info(f"Identified {len(factors)} factors")
        
        # STEP 3: Analyze reason sentiment/urgency
        sentiment = self.ai_service.analyze_leave_reason_sentiment(request.reason)
        
        # Add priority factor if urgent
        if sentiment and sentiment.get("priority") == "high":
            factors.append(Factor(
                type=FactorType.PRIORITY,
                message=f"Leave reason categorized as high priority: {sentiment.get('category').title()}",
                severity=0.0  # High priority is a 'good' factor for approval
            ))
            
        # STEP 4: Generate recommendation using rules engine
        recommendation = self.rules_engine.determine_recommendation(
            availability_pct, days_until, factors, employee_history, sentiment
        )
        
        confidence_score = self.rules_engine.calculate_confidence(
            recommendation, availability_pct, factors
        )
        
        logger.info(f"Recommendation: {recommendation.value} (confidence: {confidence_score})")
        
        # STEP 4: Generate AI summary
        ai_summary = self.ai_service.generate_manager_briefing(
            request=request,
            recommendation=recommendation,
            availability_pct=availability_pct,
            overlapping_count=overlapping_count,
            total_team_size=total_team_size,
            factors=factors,
            days_until=days_until,
            leave_duration=leave_duration
        )
        
        # STEP 5: Construct output
        output = AnalyzeLeaveOutput(
            recommendation=recommendation,
            confidence_score=confidence_score,
            factors=factors,
            ai_summary=ai_summary,
            team_availability_percentage=availability_pct,
            overlapping_members=overlapping_count,
            days_until_leave=days_until,
            total_leave_days=leave_duration,
            team_context=team_context
        )
        
        logger.info(f"Analysis complete for {request.emp_id}")
        return output
    
    async def analyze_with_auto_context(
        self,
        request: LeaveRequest,
        use_mock_data: bool = True
    ) -> AnalyzeLeaveOutput:
        """
        Analyze leave request with automatically fetched team context
        
        This is a convenience method that fetches team context from mock data
        
        Args:
            request: Leave request to analyze
            use_mock_data: Whether to use mock data (default True)
        
        Returns:
            Complete analysis with recommendation
        """
        if not use_mock_data or not self.data_service.is_data_loaded():
            raise ValueError("Mock data not available. Please provide team_context manually.")
        
        # Fetch team context from mock data
        team_context = self.data_service.get_approved_leaves_for_department(
            request.dept_id,
            start_date=request.start,
            end_date=request.end
        )
        
        # Get team size from mock data
        total_team_size = self.data_service.get_team_size(request.dept_id)
        if total_team_size == 0:
            raise ValueError(f"Department {request.dept_id} not found in mock data")
        
        # Create input
        input_data = AnalyzeLeaveInput(
            request=request,
            team_context=team_context,
            total_team_size=total_team_size
        )
        
        return await self.analyze_leave_request(input_data)


# Global service instance
leave_analysis_service = LeaveAnalysisService()
