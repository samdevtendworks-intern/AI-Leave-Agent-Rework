"""
Leave Review Agent - Manager Dashboard
Streamlit Frontend for Leave Request Analysis
"""
import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.figure_factory as ff
import plotly.graph_objects as go
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="Leave Review Agent - Manager Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .recommendation-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
        font-size: 18px;
    }
    .strongly-approve {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #28a745;
    }
    .approve {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 2px solid #17a2b8;
    }
    .review-required {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffc107;
    }
    .suggest-rejection {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #dc3545;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    .factor-item {
        padding: 10px;
        margin: 5px 0;
        border-left: 4px solid #007bff;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


class APIClient:
    """Client for interacting with the Leave Agent API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def health_check(self) -> Dict:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_departments(self) -> List[Dict]:
        """Get list of departments"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/departments")
            response.raise_for_status()
            return response.json()["departments"]
        except Exception as e:
            st.error(f"Error fetching departments: {e}")
            return []
    
    def analyze_leave_simple(self, leave_data: Dict) -> Optional[Dict]:
        """Analyze leave request (simple mode)"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze-leave-simple",
                json=leave_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error analyzing leave: {e}")
            return None
    
    def analyze_leave_full(self, leave_data: Dict) -> Optional[Dict]:
        """Analyze leave request (full mode with context)"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze-leave",
                json=leave_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error analyzing leave: {e}")
            return None


def render_recommendation_box(recommendation: str):
    """Render recommendation with appropriate styling"""
    class_map = {
        "STRONGLY_APPROVE": "strongly-approve",
        "APPROVE": "approve",
        "REVIEW_REQUIRED": "review-required",
        "SUGGEST_REJECTION": "suggest-rejection"
    }
    
    emoji_map = {
        "STRONGLY_APPROVE": "✅",
        "APPROVE": "👍",
        "REVIEW_REQUIRED": "⚠️",
        "SUGGEST_REJECTION": "❌"
    }
    
    text_map = {
        "STRONGLY_APPROVE": "STRONGLY APPROVE",
        "APPROVE": "APPROVE",
        "REVIEW_REQUIRED": "REVIEW REQUIRED",
        "SUGGEST_REJECTION": "SUGGEST REJECTION"
    }
    
    css_class = class_map.get(recommendation, "review-required")
    emoji = emoji_map.get(recommendation, "⚠️")
    text = text_map.get(recommendation, recommendation)
    
    st.markdown(
        f'<div class="recommendation-box {css_class}">{emoji} {text}</div>',
        unsafe_allow_html=True
    )


def render_confidence_gauge(confidence: float):
    """Render confidence score as a gauge"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        title={'text': "Confidence Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 80], 'color': "gray"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig


def render_team_capacity_chart(availability_pct: float):
    """Render team capacity visualization"""
    unavailable = 100 - availability_pct
    
    fig = go.Figure(data=[
        go.Bar(
            x=[availability_pct, unavailable],
            y=['Team Capacity', 'Team Capacity'],
            orientation='h',
            marker=dict(
                color=['#28a745', '#dc3545']
            ),
            text=[f'{availability_pct:.1f}% Available', f'{unavailable:.1f}% Absent'],
            textposition='inside',
            hoverinfo='text'
        )
    ])
    
    fig.update_layout(
        title="Team Availability",
        xaxis_title="Percentage",
        showlegend=False,
        height=200,
        barmode='stack'
    )
    
    return fig


def render_gantt_chart(leave_request: Dict, team_context: List[Dict]):
    """Render high-performance Gantt chart showing team schedule"""
    # Prepare data for Plotly Timeline
    plot_data = []
    
    # Add the current request
    plot_data.append(dict(
        Task=f"🔴 {leave_request['emp_id']} (REQ)",
        Start=leave_request['start'],
        Finish=leave_request['end'],
        Resource='Requested Leave',
        Color='rgb(220, 53, 69)'
    ))
    
    # Add team context
    for leave in team_context:
        plot_data.append(dict(
            Task=f"⚫ {leave['emp_id']}",
            Start=leave['start'],
            Finish=leave['end'],
            Resource='Already Approved',
            Color='rgb(108, 117, 125)'
        ))
    
    if plot_data:
        df = pd.DataFrame(plot_data)
        df['Start'] = pd.to_datetime(df['Start'])
        df['Finish'] = pd.to_datetime(df['Finish'])
        
        fig = go.Figure()
        
        for resource in df['Resource'].unique():
            df_res = df[df['Resource'] == resource]
            fig.add_trace(go.Bar(
                base=df_res['Start'],
                x=df_res['Finish'] - df_res['Start'],
                y=df_res['Task'],
                orientation='h',
                name=resource,
                marker_color=df_res['Color'].iloc[0],
                hovertemplate="<b>%{y}</b><br>Start: %{base|%Y-%m-%d}<br>End: %{x|%Y-%m-%d}<extra></extra>"
            ))
            
        fig.update_layout(
            title='Team Schedule - Leave Overlap View',
            barmode='overlay',
            height=300 + (len(plot_data) * 20),
            showlegend=True,
            xaxis_type='date',
            yaxis=dict(autorange="reversed")
        )
        return fig
    
    return None


def render_factors_list(factors: List[Dict]):
    """Render list of factors affecting the decision"""
    if not factors:
        st.info("No significant factors identified.")
        return
    
    st.subheader("📊 Decision Factors")
    
    for idx, factor in enumerate(factors, 1):
        factor_type = factor.get('type', 'UNKNOWN')
        message = factor.get('message', '')
        severity = factor.get('severity', 0)
        
        # Emoji based on type
        emoji_map = {
            'CAPACITY_RISK': '⚠️',
            'BURNOUT_RISK': '😰',
            'BEHAVIOR': '📈',
            'WEEKEND_EXTENSION': '📅',
            'SHORT_NOTICE': '⏰',
            'POLICY_VIOLATION': '❌'
        }
        
        emoji = emoji_map.get(factor_type, '•')
        
        # Severity color
        if severity >= 0.8:
            color = "red"
        elif severity >= 0.5:
            color = "orange"
        else:
            color = "blue"
        
        st.markdown(
            f'<div class="factor-item" style="border-left-color: {color};">'
            f'{emoji} <strong>{factor_type.replace("_", " ").title()}</strong><br>'
            f'{message}'
            f'</div>',
            unsafe_allow_html=True
        )


def main():
    """Main Streamlit application"""
    
    # Initialize API client
    api = APIClient(API_BASE_URL)
    
    # Header
    st.title("📋 Leave Review Agent - Manager Dashboard")
    st.markdown("*AI-Assisted Leave Request Analysis & Recommendation System*")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Health Check
        health = api.health_check()
        if health.get("status") == "healthy":
            st.success("✅ API Connected")
            if health.get("gemini_configured"):
                st.info("🤖 AI Enhanced Mode")
            else:
                st.warning("📝 Fallback Mode (No Gemini)")
        else:
            st.error("❌ API Disconnected")
            st.stop()
        
        st.markdown("---")
        
        # Mode selection
        analysis_mode = st.radio(
            "Analysis Mode",
            ["Simple (Auto-Context)", "Advanced (Manual Context)"],
            help="Simple mode automatically fetches team context from mock data"
        )
        
        st.markdown("---")
        st.caption("💡 **Tip**: Use Simple mode for quick analysis")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📝 New Leave Request", "📊 Team Overview", "ℹ️ About"])
    
    with tab1:
        st.header("Analyze Leave Request")
        
        # Get departments
        departments = api.get_departments()
        dept_options = [d["dept_id"] for d in departments]
        
        if not dept_options:
            st.error("No departments available. Please check the API.")
            st.stop()
        
        # Leave request form
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Employee Information")
            emp_id = st.text_input(
                "Employee ID",
                value="E105",
                help="Enter employee ID (e.g., E105)"
            )
            
            dept_id = st.selectbox(
                "Department",
                options=dept_options,
                help="Select employee's department"
            )
            
            reason = st.text_area(
                "Leave Reason",
                value="Family wedding",
                help="Enter the reason for leave"
            )
        
        with col2:
            st.subheader("📅 Leave Dates")
            
            today = date.today()
            
            start_date = st.date_input(
                "Start Date",
                value=today + timedelta(days=7),
                min_value=today,
                help="Leave start date"
            )
            
            end_date = st.date_input(
                "End Date",
                value=today + timedelta(days=9),
                min_value=start_date,
                help="Leave end date"
            )
            
            # Calculate duration
            duration = (end_date - start_date).days + 1
            st.metric("Duration", f"{duration} days")
        
        # Advanced mode: Manual team context
        if "Advanced" in analysis_mode:
            st.markdown("---")
            st.subheader("👥 Team Context (Manual)")
            
            team_size = st.number_input(
                "Total Team Size",
                min_value=1,
                max_value=50,
                value=5,
                help="Total number of people in the team"
            )
            
            st.write("**Team Members Already on Leave:**")
            
            num_overlaps = st.number_input(
                "Number of overlapping leaves",
                min_value=0,
                max_value=10,
                value=0,
                help="How many team members are already on leave during this period?"
            )
            
            team_context = []
            if num_overlaps > 0:
                for i in range(num_overlaps):
                    with st.expander(f"Team Member {i+1}"):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            tm_emp_id = st.text_input(
                                "Employee ID",
                                value=f"E{100+i}",
                                key=f"tm_emp_{i}"
                            )
                        with col_b:
                            tm_start = st.date_input(
                                "Start",
                                value=start_date,
                                key=f"tm_start_{i}"
                            )
                        with col_c:
                            tm_end = st.date_input(
                                "End",
                                value=end_date,
                                key=f"tm_end_{i}"
                            )
                        
                        team_context.append({
                            "emp_id": tm_emp_id,
                            "start": tm_start.isoformat(),
                            "end": tm_end.isoformat()
                        })
        
        # Analyze button
        st.markdown("---")
        analyze_button = st.button("🔍 Analyze Leave Request", type="primary", use_container_width=True)
        
        if analyze_button:
            with st.spinner("Analyzing leave request..."):
                
                # Prepare request data
                if "Simple" in analysis_mode:
                    leave_data = {
                        "emp_id": emp_id,
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                        "reason": reason,
                        "dept_id": dept_id
                    }
                    result = api.analyze_leave_simple(leave_data)
                else:
                    leave_data = {
                        "request": {
                            "emp_id": emp_id,
                            "start": start_date.isoformat(),
                            "end": end_date.isoformat(),
                            "reason": reason,
                            "dept_id": dept_id
                        },
                        "team_context": team_context,
                        "total_team_size": team_size
                    }
                    result = api.analyze_leave_full(leave_data)
                
                if result:
                    st.success("✅ Analysis Complete!")
                    st.markdown("---")
                    
                    # Display recommendation
                    st.subheader("🎯 Recommendation")
                    render_recommendation_box(result['recommendation'])
                    
                    # Metrics row
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Confidence",
                            f"{result['confidence_score']*100:.0f}%",
                            help="System confidence in this recommendation"
                        )
                    
                    with col2:
                        st.metric(
                            "Team Availability",
                            f"{result['team_availability_percentage']:.1f}%",
                            help="Percentage of team available during leave period"
                        )
                    
                    with col3:
                        st.metric(
                            "Notice Period",
                            f"{result['days_until_leave']} days",
                            help="Days between now and leave start"
                        )
                    
                    with col4:
                        st.metric(
                            "Overlapping",
                            f"{result['overlapping_members']} members",
                            help="Team members already on leave"
                        )
                    
                    st.markdown("---")
                    
                    # Two column layout
                    col_left, col_right = st.columns([1, 1])
                    
                    with col_left:
                        # AI Summary
                        st.subheader("🤖 AI Analysis")
                        st.info(result['ai_summary'])
                        
                        # Factors
                        render_factors_list(result['factors'])
                    
                    with col_right:
                        # Visualizations
                        st.subheader("📊 Visualizations")
                        
                        # Confidence gauge
                        confidence_fig = render_confidence_gauge(result['confidence_score'])
                        st.plotly_chart(confidence_fig, use_container_width=True)
                        
                        # Team capacity
                        capacity_fig = render_team_capacity_chart(
                            result['team_availability_percentage']
                        )
                        st.plotly_chart(capacity_fig, use_container_width=True)
                    
                    # Gantt chart (full width)
                    st.markdown("---")
                    gantt_fig = render_gantt_chart(
                        leave_data.get('request', leave_data),
                        result.get('team_context', [])
                    )
                    if gantt_fig:
                        st.plotly_chart(gantt_fig, use_container_width=True)
                    else:
                        st.info("No overlaps detected during this period.")
                    
                    # Action buttons
                    st.markdown("---")
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("✅ Approve", type="primary", use_container_width=True):
                            st.success("Leave request approved!")
                    
                    with col_btn2:
                        if st.button("❌ Reject", type="secondary", use_container_width=True):
                            st.error("Leave request rejected!")
                    
                    with col_btn3:
                        if st.button("💬 Request More Info", use_container_width=True):
                            st.info("Additional information requested from employee")
    
    with tab2:
        st.header("👥 Team Overview")
        
        # Get departments
        departments = api.get_departments()
        
        if departments:
            st.subheader("Department Statistics")
            
            # Create DataFrame
            df = pd.DataFrame(departments)
            
            # Display as table
            st.dataframe(
                df,
                column_config={
                    "dept_id": st.column_config.TextColumn("Department", width="medium"),
                    "team_size": st.column_config.NumberColumn("Team Size", width="small")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Chart
            fig = go.Figure(data=[
                go.Bar(
                    x=[d['dept_id'] for d in departments],
                    y=[d['team_size'] for d in departments],
                    marker_color='lightblue'
                )
            ])
            
            fig.update_layout(
                title="Team Size by Department",
                xaxis_title="Department",
                yaxis_title="Team Size",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No department data available")
    
    with tab3:
        st.header("ℹ️ About the System")
        
        st.markdown("""
        ### AI-Assisted Leave Review Agent
        
        This system helps managers make informed decisions about leave requests by analyzing:
        
        #### 🎯 **Key Features**
        - **Team Capacity Analysis**: Real-time calculation of available workforce
        - **Behavioral Pattern Detection**: Identifies burnout risks and leave patterns
        - **AI-Powered Insights**: Context-aware recommendations using Google Gemini
        - **Visual Analytics**: Interactive charts and Gantt timeline views
        
        #### 📊 **Recommendation Levels**
        - **✅ STRONGLY APPROVE**: Burnout risk detected - prioritize employee wellbeing
        - **👍 APPROVE**: Sufficient capacity, no concerns identified
        - **⚠️ REVIEW REQUIRED**: Manual judgment needed due to constraints
        - **❌ SUGGEST REJECTION**: Critical capacity issues or policy violations
        
        #### 🔍 **Decision Factors**
        The system considers:
        - Team availability percentage
        - Notice period (days in advance)
        - Historical leave patterns
        - Weekend extension patterns
        - Burnout risk indicators
        - Unplanned leave frequency
        
        #### ⚙️ **Business Rules**
        - Minimum team capacity: 70%
        - Burnout threshold: 6 months without leave
        - Short notice: Less than 7 days
        - Critical capacity: Less than 50% availability
        
        ---
        
        **Version**: 1.0.0  
        **Organization**: Tendworks Private Limited  
        **Project**: Next-Gen HRMS Intelligence Initiative
        """)


if __name__ == "__main__":
    main()
