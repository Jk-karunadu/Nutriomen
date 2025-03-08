import os
import streamlit as st
import sqlite3
from datetime import datetime
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMHelper:
    """Helper class to interact with ChatGroq's Llama3 model."""
    def __init__(self):
        self.llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-8b-8192")
    
    def get_response(self, prompt):
        """Send the prompt to ChatGroq and return the response."""
        response = self.llm.invoke(prompt)
        return response.content  # Extract and return the response content

def get_profile(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    
    if result:
        columns = [desc[0] for desc in c.description]
        profile = {columns[i]: result[i] for i in range(len(columns))}
        return profile
    return None

def generate_nutrition_prompt(profile):
    """Generate a prompt for the LLM based on the user's profile data."""
    
    # Calculate BMI
    bmi = profile['weight'] / ((profile['height'] / 100) ** 2)
    bmi_status = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    
    # Format menstruation information
    if profile['menstruation_date']:
        # Fix: Calculate days since period without calling .date()
        menstruation_date = datetime.strptime(profile['menstruation_date'], '%Y-%m-%d')
        days_since_period = (datetime.now() - menstruation_date).days
        period_info = f"Last menstruation started {days_since_period} days ago. Has a {'regular' if profile['is_regular_cycle'] else 'irregular'} cycle."
    else:
        period_info = "No menstruation data provided."
    
    # Compile prompt
    prompt = f"""
    You are a professional nutrition advisor specializing in women's health. Provide personalized nutrition advice for a woman with the following profile:
    
    Age: {profile['age']} years
    Height: {profile['height']} cm
    Weight: {profile['weight']} kg
    BMI: {bmi:.1f} ({bmi_status})
    Education: {profile['education']}
    Menstruation: {period_info}
    Pregnant: {'Yes, week ' + str(profile['pregnancy_week']) if profile['is_pregnant'] else 'No'}
    Medical conditions: {profile['diseases'] if profile['diseases'] else 'None reported'}
    Food allergies/intolerances: {profile['food_allergies'] if profile['food_allergies'] else 'None reported'}
    
    Provide 5-7 specific, actionable nutrition tips that address her unique needs. Format each tip as a bullet point and add attractive emojis. Focus on:
    1. Key nutrients she should prioritize
    2. Foods that would be beneficial
    3. Dietary patterns that may help with any health concerns
    4. Specific recommendations related to her reproductive health status
    
    Keep the tips concise, practical, and evidence-based. 
    """
    
    return prompt

def dashboard_page(conn):
    st.title(f"Welcome, {st.session_state.username}! 👋")
    
    # Get user profile to check if it's complete
    profile = get_profile(conn, st.session_state.user_id)
    
    if profile:
        st.write("Your nutrition profile is set up! Here's a summary:")
        
        # Calculate BMI
        bmi = profile['weight'] / ((profile['height'] / 100) ** 2)
        bmi_status = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Age", f"{profile['age']} years")
        with col2:
            st.metric("BMI", f"{bmi:.1f}", bmi_status)
        with col3:
            if profile['is_pregnant']:
                st.metric("Pregnancy", f"Week {profile['pregnancy_week']}")
            else:
                st.metric("Weight", f"{profile['weight']} kg")
        
        st.write("Visit the profile section to update your information.")
        
        # Show personalized nutrition tips
        st.subheader("Personalized Nutrition Tips")
        
        # Check if we should use the LLM for tips
        if "llm_tips" not in st.session_state:
            st.session_state.llm_tips = None
        
        # Add a refresh button to get new LLM-generated tips
        if st.button("Get Nutrition Advice"):
            with st.spinner("Generating personalized nutrition tips..."):
                try:
                    # Initialize the LLM helper
                    llm_helper = LLMHelper()
                    
                    # Generate the prompt based on the user's profile
                    prompt = generate_nutrition_prompt(profile)
                    
                    # Get the response from the LLM
                    llm_response = llm_helper.get_response(prompt)
                    
                    # Store the response in session state
                    st.session_state.llm_tips = llm_response
                except Exception as e:
                    st.error(f"Error generating nutrition tips: {e}")
                    st.session_state.llm_tips = None
        
        # Display LLM-generated tips if available
        if st.session_state.llm_tips:
            st.markdown(st.session_state.llm_tips)
            st.caption("Tips generated by AI based on your profile data")
        else:
            # Fallback to basic tips if LLM isn't used or fails
            tips = []
            
            if profile['is_pregnant']:
                tips.append("- Ensure adequate folic acid intake for healthy fetal development")
                tips.append("- Increase calcium consumption for bone health")
            
            if profile['age'] > 50:
                tips.append("- Consider vitamin D and calcium supplements for bone health")
            
            if bmi < 18.5:
                tips.append("- Focus on nutrient-dense foods to reach a healthy weight")
            elif bmi > 25:
                tips.append("- Consider balanced portion control while maintaining nutrient intake")
            
            if profile['is_regular_cycle'] == 0:
                tips.append("- Iron-rich foods may help with irregular menstruation")
            
            if tips:
                for tip in tips:
                    st.write(tip)
            else:
                st.write("Click 'Get Nutrition Advice' for personalized recommendations.")
        
        # Add informational note
        st.info("Nutrition advice is general in nature. For medical or specific dietary concerns, please consult a healthcare professional.")
    
    else:
        st.info("Please complete your profile to get personalized nutrition advice.")
        if st.button("Set Up Profile Now"):
            st.session_state.page = "profile"
            st.experimental_rerun()