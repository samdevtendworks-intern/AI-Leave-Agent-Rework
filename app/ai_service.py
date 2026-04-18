"""
AI Service
Integration with Google Gemini for intelligent analysis and recommendations
"""
import google.generativeai as genai
from typing import Optional, List
from app.config import settings
from app.models import LeaveRequest, Factor, RecommendationType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    """Handles AI-powered analysis using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini AI service"""
        self.configured = False
        self.model = None
        
        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.configured = True
                logger.info("✅ Gemini AI configured successfully")
            except Exception as e:
                logger.error(f"❌ Failed to configure Gemini: {e}")
                self.configured = False
        else:
            logger.warning("⚠️  Gemini API key not provided. AI features disabled.")
    
    def is_configured(self) -> bool:
        """Check if AI service is properly configured"""
        return self.configured
    
    def generate_manager_briefing(
        self,
        request: LeaveRequest,
        recommendation: RecommendationType,
        availability_pct: float,
        overlapping_count: int,
        total_team_size: int,
        factors: List[Factor],
        days_until: int,
        leave_duration: int
    ) -> str:
        """
        Generate an intelligent manager briefing using Gemini
        
        Args:
            request: Leave request details
            recommendation: System recommendation
            availability_pct: Team availability percentage
            overlapping_count: Number of overlapping absences
            total_team_size: Total team size
            factors: List of factors affecting decision
            days_until: Days until leave starts
            leave_duration: Duration of leave in days
        
        Returns:
            AI-generated summary for the manager
        """
        if not self.configured:
            return self._fallback_summary(
                recommendation, availability_pct, overlapping_count, request.reason
            )
        
        # Construct detailed prompt for Gemini
        prompt = self._build_prompt(
            request, recommendation, availability_pct, overlapping_count,
            total_team_size, factors, days_until, leave_duration
        )
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_summary(
                recommendation, availability_pct, overlapping_count, request.reason
            )
    
    def _build_prompt(
        self,
        request: LeaveRequest,
        recommendation: RecommendationType,
        availability_pct: float,
        overlapping_count: int,
        total_team_size: int,
        factors: List[Factor],
        days_until: int,
        leave_duration: int
    ) -> str:
        """Build detailed prompt for Gemini"""
        
        # Format factors
        factors_text = "\n".join([
            f"- {f.type.value}: {f.message}"
            for f in factors
        ])
        
        prompt = f"""You are an intelligent HR assistant helping a manager review a leave request.

LEAVE REQUEST DETAILS:
- Employee ID: {request.emp_id}
- Department: {request.dept_id}
- Leave Dates: {request.start} to {request.end} ({leave_duration} days)
- Notice Period: {days_until} days in advance
- Reason: "{request.reason}"

TEAM IMPACT ANALYSIS:
- Total Team Size: {total_team_size}
- Already Absent: {overlapping_count} team members
- Team Availability: {availability_pct}%
- Remaining Available: {total_team_size - overlapping_count - 1} members

IDENTIFIED FACTORS:
{factors_text if factors else "No significant concerns identified."}

SYSTEM RECOMMENDATION: {recommendation.value}

TASK:
Generate a concise, professional briefing (2-3 sentences) for the manager that:
1. Acknowledges the employee's reason
2. Highlights the key team impact
3. Provides actionable guidance

Keep the tone professional, empathetic, and data-driven. Focus on helping the manager make an informed decision."""

        return prompt
    
    def _fallback_summary(
        self,
        recommendation: RecommendationType,
        availability_pct: float,
        overlapping_count: int,
        reason: str
    ) -> str:
        """Generate fallback summary when AI is not available"""
        
        # Analyze reason sentiment
        reason_lower = reason.lower()
        is_urgent = any(word in reason_lower for word in [
            'emergency', 'urgent', 'medical', 'sick', 'hospital'
        ])
        
        if recommendation == RecommendationType.STRONGLY_APPROVE:
            return f"Employee hasn't taken leave in over 6 months, indicating burnout risk. Strongly recommend approval to support employee wellbeing."
        
        elif recommendation == RecommendationType.SUGGEST_REJECTION:
            if is_urgent:
                return f"While the reason ('{reason}') appears urgent, team capacity is critically low at {availability_pct}%. Consider shorter duration or emergency coverage arrangements."
            else:
                return f"Team capacity drops to {availability_pct}% with {overlapping_count} members already absent. Recommend rejecting or requesting alternate dates."
        
        elif recommendation == RecommendationType.REVIEW_REQUIRED:
            if is_urgent:
                return f"The reason appears urgent ('{reason}'), but {overlapping_count} team members are already absent. Manual review needed to balance employee needs with team capacity."
            else:
                return f"Team availability at {availability_pct}% requires careful consideration. Review if the dates can be adjusted or if coverage can be arranged."
        
        else:  # APPROVE
            return f"Team has sufficient capacity ({availability_pct}% available) to accommodate this leave. Recommend approval."
    
    def analyze_leave_reason_sentiment(self, reason: str) -> dict:
        """
        Analyze the sentiment and urgency of leave reason
        
        Args:
            reason: Leave reason text
        
        Returns:
            Dictionary with sentiment analysis
        """
        reason_lower = reason.lower()
        
        # Simple keyword-based analysis (can be enhanced with Gemini)
        urgency_keywords = ['emergency', 'urgent', 'critical', 'immediate', 'hospital', 'sick']
        personal_keywords = ['family', 'wedding', 'personal', 'home']
        leisure_keywords = ['vacation', 'holiday', 'travel', 'tour']
        
        is_urgent = any(word in reason_lower for word in urgency_keywords)
        is_personal = any(word in reason_lower for word in personal_keywords)
        is_leisure = any(word in reason_lower for word in leisure_keywords)
        
        if is_urgent:
            category = "urgent"
            priority = "high"
        elif is_personal:
            category = "personal"
            priority = "medium"
        elif is_leisure:
            category = "leisure"
            priority = "low"
        else:
            category = "unspecified"
            priority = "medium"
        
        return {
            "category": category,
            "priority": priority,
            "is_urgent": is_urgent
        }


# Global AI service instance
ai_service = AIService()
