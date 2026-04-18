"""
Data Models
Pydantic models for request validation and response serialization
"""
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Optional
from datetime import date
from enum import Enum


class RecommendationType(str, Enum):
    """Recommendation types for leave requests"""
    STRONGLY_APPROVE = "STRONGLY_APPROVE"
    APPROVE = "APPROVE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    SUGGEST_REJECTION = "SUGGEST_REJECTION"


class FactorType(str, Enum):
    """Types of factors affecting the recommendation"""
    CAPACITY_RISK = "CAPACITY_RISK"
    BEHAVIOR = "BEHAVIOR"
    BURNOUT_RISK = "BURNOUT_RISK"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    WEEKEND_EXTENSION = "WEEKEND_EXTENSION"
    SHORT_NOTICE = "SHORT_NOTICE"
    PRIORITY = "PRIORITY"


class LeaveRequest(BaseModel):
    """Leave request details from employee"""
    emp_id: str = Field(..., description="Employee ID")
    start: date = Field(..., description="Leave start date")
    end: date = Field(..., description="Leave end date")
    reason: str = Field(..., description="Reason for leave")
    dept_id: str = Field(..., description="Department ID")
    
    @field_validator('end')
    def end_after_start(cls, v: date, info: ValidationInfo) -> date:
        if 'start' in info.data and v < info.data['start']:
            raise ValueError('end date must be after start date')
        return v


class TeamMemberLeave(BaseModel):
    """Existing approved leave for a team member"""
    emp_id: str = Field(..., description="Employee ID")
    start: date = Field(..., description="Leave start date")
    end: date = Field(..., description="Leave end date")


class AnalyzeLeaveInput(BaseModel):
    """Input for leave analysis API"""
    request: LeaveRequest
    team_context: List[TeamMemberLeave] = Field(default_factory=list)
    total_team_size: int = Field(..., gt=0, description="Total team size")


class Factor(BaseModel):
    """Individual factor affecting the recommendation"""
    type: FactorType
    message: str
    severity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Severity score 0-1")


class AnalyzeLeaveOutput(BaseModel):
    """Output from leave analysis"""
    recommendation: RecommendationType
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    factors: List[Factor]
    ai_summary: str
    
    # Additional analytics
    team_availability_percentage: float
    overlapping_members: int
    days_until_leave: int
    total_leave_days: int
    team_context: List[TeamMemberLeave] = []


class EmployeeHistory(BaseModel):
    """Historical leave data for an employee"""
    emp_id: str
    total_leaves_taken: int
    unplanned_leaves: int
    weekend_extensions: int
    last_leave_date: Optional[date] = None
    months_since_last_leave: Optional[float] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    gemini_configured: bool
