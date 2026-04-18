"""
Data Service
Handles loading and querying mock data for team schedules and employee history
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import date
from app.models import EmployeeHistory, TeamMemberLeave
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataService:
    """Service for managing mock data"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data service
        
        Args:
            data_dir: Directory containing mock data files
        """
        self.data_dir = Path(data_dir)
        self.team_schedules = {}
        self.employee_histories = {}
        self.loaded = False
        
        # Try to load data
        self.load_data()
    
    def load_data(self) -> bool:
        """
        Load mock data from JSON files
        
        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            # Load team schedules
            schedules_file = self.data_dir / "team_schedules.json"
            if schedules_file.exists():
                with open(schedules_file, 'r') as f:
                    self.team_schedules = json.load(f)
                logger.info(f"✅ Loaded team schedules for {len(self.team_schedules)} departments")
            else:
                logger.warning(f"⚠️  Team schedules file not found: {schedules_file}")
            
            # Load employee histories
            histories_file = self.data_dir / "employee_histories.json"
            if histories_file.exists():
                with open(histories_file, 'r') as f:
                    self.employee_histories = json.load(f)
                logger.info(f"✅ Loaded history for {len(self.employee_histories)} employees")
            else:
                logger.warning(f"⚠️  Employee histories file not found: {histories_file}")
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            self.loaded = False
            return False
    
    def get_team_schedule(self, dept_id: str) -> Optional[Dict]:
        """
        Get team schedule for a department
        
        Args:
            dept_id: Department ID
        
        Returns:
            Team schedule data or None
        """
        return self.team_schedules.get(dept_id)
    
    def get_approved_leaves_for_department(
        self,
        dept_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TeamMemberLeave]:
        """
        Get approved leaves for a department, optionally filtered by date range
        
        Args:
            dept_id: Department ID
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            List of TeamMemberLeave objects
        """
        schedule = self.get_team_schedule(dept_id)
        if not schedule:
            return []
        
        leaves = []
        for leave_data in schedule.get('approved_leaves', []):
            leave_start = date.fromisoformat(leave_data['start'])
            leave_end = date.fromisoformat(leave_data['end'])
            
            # Filter by date range if provided
            if start_date and end_date:
                # Check if leave overlaps with the requested range
                if leave_end >= start_date and leave_start <= end_date:
                    leaves.append(TeamMemberLeave(
                        emp_id=leave_data['emp_id'],
                        start=leave_start,
                        end=leave_end
                    ))
            else:
                leaves.append(TeamMemberLeave(
                    emp_id=leave_data['emp_id'],
                    start=leave_start,
                    end=leave_end
                ))
        
        return leaves
    
    def get_employee_history(self, emp_id: str) -> Optional[EmployeeHistory]:
        """
        Get leave history for an employee
        
        Args:
            emp_id: Employee ID
        
        Returns:
            EmployeeHistory object or None
        """
        history_data = self.employee_histories.get(emp_id)
        if not history_data:
            return None
        
        # Convert to EmployeeHistory model
        return EmployeeHistory(
            emp_id=history_data['emp_id'],
            total_leaves_taken=history_data['total_leaves_taken'],
            unplanned_leaves=history_data['unplanned_leaves'],
            weekend_extensions=history_data['weekend_extensions'],
            last_leave_date=date.fromisoformat(history_data['last_leave_date']) if history_data.get('last_leave_date') else None,
            months_since_last_leave=history_data.get('months_since_last_leave')
        )
    
    def get_team_size(self, dept_id: str) -> int:
        """
        Get total team size for a department
        
        Args:
            dept_id: Department ID
        
        Returns:
            Team size or 0 if not found
        """
        schedule = self.get_team_schedule(dept_id)
        if schedule:
            return schedule.get('team_size', 0)
        return 0
    
    def is_data_loaded(self) -> bool:
        """Check if data is loaded"""
        return self.loaded
    
    def get_all_departments(self) -> List[str]:
        """Get list of all department IDs"""
        return list(self.team_schedules.keys())
    
    def get_statistics(self) -> Dict:
        """Get data statistics"""
        return {
            "departments": len(self.team_schedules),
            "employees_with_history": len(self.employee_histories),
            "total_approved_leaves": sum(
                len(schedule.get('approved_leaves', []))
                for schedule in self.team_schedules.values()
            )
        }


# Global data service instance
data_service = DataService()
