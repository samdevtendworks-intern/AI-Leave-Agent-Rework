"""
Mock Data Generator
Generates realistic mock data for team schedules and employee history
"""
import json
from datetime import date, timedelta
from typing import List, Dict
import random
from pathlib import Path


class MockDataGenerator:
    """Generate mock data for testing the leave agent"""
    
    def __init__(self):
        self.departments = ["ENG_BACKEND", "ENG_FRONTEND", "DATA_SCIENCE", "DEVOPS", "QA"]
        self.leave_reasons = [
            "Family wedding",
            "Medical emergency",
            "Personal work",
            "Vacation",
            "Sick leave",
            "Child care",
            "Home maintenance",
            "Attending conference",
            "Family emergency"
        ]
    
    def generate_employee_id(self, num: int) -> str:
        """Generate employee ID"""
        return f"E{num:03d}"
    
    def generate_team_schedule(self, dept_id: str, team_size: int, 
                               days_range: int = 60) -> List[Dict]:
        """
        Generate team schedule with approved leaves
        
        Args:
            dept_id: Department ID
            team_size: Number of team members
            days_range: Number of days to generate data for
        
        Returns:
            List of approved leave records
        """
        approved_leaves = []
        today = date.today()
        
        for emp_num in range(100, 100 + team_size):
            emp_id = self.generate_employee_id(emp_num)
            
            # Generate 2-4 leave periods for each employee
            num_leaves = random.randint(2, 4)
            
            for _ in range(num_leaves):
                # Random start date within range
                days_offset = random.randint(-30, days_range)
                start_date = today + timedelta(days=days_offset)
                
                # Random leave duration (1-7 days)
                duration = random.randint(1, 7)
                end_date = start_date + timedelta(days=duration - 1)
                
                # Random reason
                reason = random.choice(self.leave_reasons)
                
                approved_leaves.append({
                    "emp_id": emp_id,
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "reason": reason,
                    "dept_id": dept_id,
                    "status": "APPROVED"
                })
        
        return approved_leaves
    
    def generate_employee_history(self, emp_id: str, 
                                  months_back: int = 12) -> Dict:
        """
        Generate employee leave history with behavioral patterns
        
        Args:
            emp_id: Employee ID
            months_back: Number of months of history
        
        Returns:
            Dictionary with employee leave history
        """
        today = date.today()
        
        # Simulate different behavioral patterns
        pattern_type = random.choice([
            "regular",      # Normal behavior
            "weekend_lover", # Frequently extends weekends
            "burnout_risk",  # Hasn't taken leave in long time
            "unplanned"      # Frequently takes last-minute leave
        ])
        
        if pattern_type == "regular":
            total_leaves = random.randint(8, 15)
            unplanned = random.randint(0, 2)
            weekend_extensions = random.randint(0, 2)
            last_leave = today - timedelta(days=random.randint(20, 60))
            
        elif pattern_type == "weekend_lover":
            total_leaves = random.randint(10, 18)
            unplanned = random.randint(0, 3)
            weekend_extensions = random.randint(5, 8)  # High weekend extension
            last_leave = today - timedelta(days=random.randint(10, 30))
            
        elif pattern_type == "burnout_risk":
            total_leaves = random.randint(2, 5)  # Very few leaves
            unplanned = 0
            weekend_extensions = 0
            last_leave = today - timedelta(days=random.randint(200, 365))  # Long time ago
            
        else:  # unplanned
            total_leaves = random.randint(8, 15)
            unplanned = random.randint(4, 8)  # High unplanned leaves
            weekend_extensions = random.randint(2, 4)
            last_leave = today - timedelta(days=random.randint(15, 45))
        
        # Calculate months since last leave
        if last_leave:
            months_since = (today - last_leave).days / 30.0
        else:
            months_since = None
        
        return {
            "emp_id": emp_id,
            "total_leaves_taken": total_leaves,
            "unplanned_leaves": unplanned,
            "weekend_extensions": weekend_extensions,
            "last_leave_date": last_leave.isoformat() if last_leave else None,
            "months_since_last_leave": round(months_since, 2) if months_since else None,
            "pattern_type": pattern_type
        }
    
    def save_mock_data(self, output_dir: str = "data"):
        """Generate and save all mock data to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate team schedules for each department
        all_schedules = {}
        for dept in self.departments:
            team_size = random.randint(5, 12)
            schedule = self.generate_team_schedule(dept, team_size)
            all_schedules[dept] = {
                "team_size": team_size,
                "approved_leaves": schedule
            }
        
        # Save team schedules
        with open(output_path / "team_schedules.json", "w") as f:
            json.dump(all_schedules, f, indent=2)
        
        # Generate employee histories
        employee_histories = {}
        for emp_num in range(100, 150):
            emp_id = self.generate_employee_id(emp_num)
            history = self.generate_employee_history(emp_id)
            employee_histories[emp_id] = history
        
        # Save employee histories
        with open(output_path / "employee_histories.json", "w") as f:
            json.dump(employee_histories, f, indent=2)
        
        print(f"✅ Mock data generated successfully in {output_dir}/")
        print(f"   - team_schedules.json: {len(all_schedules)} departments")
        print(f"   - employee_histories.json: {len(employee_histories)} employees")
        
        return all_schedules, employee_histories


if __name__ == "__main__":
    # Generate mock data when run directly
    generator = MockDataGenerator()
    generator.save_mock_data("../data")
