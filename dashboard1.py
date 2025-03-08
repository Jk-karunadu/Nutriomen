import streamlit as st
import logging
from typing import Dict, Optional, List, Tuple, Any
import sqlite3

# Set up logging with a string literal instead of _name_
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dashboard")  # Use a string literal instead of _name_

def get_profile(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user profile from database.
    
    Args:
        conn: Database connection
        user_id: User ID to retrieve profile for
        
    Returns:
        Dictionary containing profile data or None if profile doesn't exist
    """
    try:
        with conn:
            c = conn.cursor()
            c.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            
            if result:
                columns = [desc[0] for desc in c.description]
                profile = {columns[i]: result[i] for i in range(len(columns))}
                return profile
            return None
    except sqlite3.Error as e:
        logger.error(f"Database error occurred: {e}")
        st.error("Failed to retrieve your profile. Please try again later.")
        return None

def calculate_bmi(weight: float, height: float) -> Tuple[float, str]:
    """
    Calculate BMI and determine status.
    
    Args:
        weight: Weight in kg
        height: Height in cm
        
    Returns:
        Tuple of (BMI value, BMI status)
    """
    try:
        bmi = weight / ((height / 100) ** 2)
        if bmi < 18.5:
            status = "Underweight"
        elif bmi < 25:
            status = "Normal"
        elif bmi < 30:
            status = "Overweight"
        else:
            status = "Obese"
        return bmi, status
    except ZeroDivisionError:
        logger.warning(f"Invalid height value (0) for BMI calculation")
        return 0, "Unknown"
    except Exception as e:
        logger.error(f"Error calculating BMI: {e}")
        return 0, "Error"

def get_personalized_tips(profile: Dict[str, Any], bmi: float) -> List[str]:
    """
    Generate personalized nutrition tips based on user profile.
    
    Args:
        profile: User profile dictionary
        bmi: Calculated BMI value
        
    Returns:
        List of personalized tips
    """
    tips = []
    
    # Pregnancy-specific tips
    if profile.get('is_pregnant'):
        trimester = 1 + (profile.get('pregnancy_week', 0) // 13)
        tips.append(f"- Ensure adequate folic acid intake for healthy fetal development (Trimester {trimester})")
        tips.append("- Increase calcium consumption for bone health")
        tips.append("- Stay well-hydrated throughout your pregnancy")
    
    # Age-specific tips
    if profile.get('age', 0) > 50:
        tips.append("- Consider vitamin D and calcium supplements for bone health")
        tips.append("- Include omega-3 rich foods for heart and brain health")
    elif profile.get('age', 0) > 30:
        tips.append("- Maintain adequate protein intake to preserve muscle mass")
    elif profile.get('age', 0) < 18:
        tips.append("- Focus on nutrient-dense foods to support growth and development")
    
    # BMI-specific tips
    if bmi < 18.5:
        tips.append("- Focus on nutrient-dense foods to reach a healthy weight")
        tips.append("- Consider protein-rich meals and healthy fats for balanced weight gain")
    elif bmi > 25:
        tips.append("- Consider balanced portion control while maintaining nutrient intake")
        tips.append("- Include regular physical activity in your routine")
    
    # Menstrual cycle tips
    if profile.get('is_regular_cycle') == 0:
        tips.append("- Iron-rich foods may help with irregular menstruation")
        tips.append("- Consider foods with magnesium and B vitamins for hormone balance")
    
    return tips

def display_profile_summary(profile: Dict[str, Any]) -> None:
    """Display a visual summary of the user's profile."""
    bmi, bmi_status = calculate_bmi(profile.get('weight', 0), profile.get('height', 0))
    
    # Create a clean, visually appealing metric display
    st.write("### Your Health Profile")
    
    # Display key metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Age", f"{profile.get('age', 'N/A')} years")
        st.metric("Height", f"{profile.get('height', 'N/A')} cm")
    
    with col2:
        st.metric("BMI", f"{bmi:.1f}", bmi_status)
        st.metric("Weight", f"{profile.get('weight', 'N/A')} kg")
    
    with col3:
        if profile.get('is_pregnant'):
            st.metric("Pregnancy", f"Week {profile.get('pregnancy_week', 'N/A')}")
            due_week = profile.get('pregnancy_week', 0) 
            weeks_remaining = 40 - due_week
            if weeks_remaining > 0:
                st.metric("Due in", f"{weeks_remaining} weeks")
        else:
            activity_level = profile.get('activity_level', 'Unknown')
            st.metric("Activity", activity_level)
    
    # Create expandable section for more details
    with st.expander("See more details"):
        st.write(f"*Gender:* {profile.get('gender', 'Not specified')}")
        st.write(f"*Dietary preferences:* {profile.get('dietary_preference', 'None specified')}")
        st.write(f"*Health conditions:* {profile.get('health_conditions', 'None specified')}")
    
    st.write("Visit the profile section to update your information.")

def dashboard_page(conn: sqlite3.Connection) -> None:
    """
    Render the user dashboard page.
    
    Args:
        conn: Database connection
    """
    # Check authentication
    if not st.session_state.get('user_id'):
        st.warning("Please log in to view your dashboard")
        return
    
    # Page header with personalized greeting
    st.title(f"Welcome, {st.session_state.get('username', 'User')}! 👋")
    
    # Main dashboard container with improved styling
    dashboard_container = st.container()
    
    with dashboard_container:
        # Get user profile with error handling
        profile = get_profile(conn, st.session_state.user_id)
        
        if profile:
            # Display profile summary
            display_profile_summary(profile)
            
            # Get BMI for tips
            bmi, _ = calculate_bmi(profile.get('weight', 0), profile.get('height', 0))
            
            # Show personalized nutrition tips
            st.subheader("Personalized Nutrition Tips")
            tips = get_personalized_tips(profile, bmi)
            
            if tips:
                # Create a visually appealing card-like display for tips
                for i, tip in enumerate(tips):
                    tip_container = st.container()
                    with tip_container:
                        st.markdown(f"{tip}")
                    if i < len(tips) - 1:
                        st.markdown("---")
            else:
                st.info("Visit the Nutrition Advice section for personalized recommendations.")
            
            # Quick actions section
            st.subheader("Quick Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Track Today's Meals"):
                    st.session_state.page = "meal_tracker"
                    st.experimental_rerun()
            with col2:
                if st.button("View Nutrition Reports"):
                    st.session_state.page = "reports"
                    st.experimental_rerun()
                    
        else:
            # Profile setup prompt with improved UX
            st.info("Please complete your profile to get personalized nutrition advice.")
            
            # Use columns to create a better layout
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("Set Up Profile Now", key="setup_profile", use_container_width=True):
                    st.session_state.page = "profile"
                    st.experimental_rerun()
            
            # Show preview of benefits
            with st.expander("Why complete your profile?"):
                st.write("- Get personalized nutrition advice based on your needs")
                st.write("- Track your progress over time")
                st.write("- Receive custom meal suggestions")
                st.write("- Set realistic health goals")