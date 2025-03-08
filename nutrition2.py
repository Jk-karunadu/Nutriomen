import streamlit as st
import pandas as pd
import numpy as np

def calculate_calories(age, bmi):
    """Calculate recommended daily calorie intake based on age and BMI."""
    if age <= 3:
        return 1000
    elif 4 <= age <= 8:
        return 1400
    elif 9 <= age <= 18:
        return 1800 if bmi < 25 else 2000
    elif 19 <= age <= 30:
        return 2000 if bmi < 25 else 2200
    elif 31 <= age <= 50:
        return 1800 if bmi < 25 else 2000
    else:
        return 1600 if bmi < 25 else 1800

def calculate_macros(calories):
    """Calculate macronutrient distribution based on total calories."""
    return {
        "Carbohydrates": (calories * 0.55) / 4,
        "Proteins": (calories * 0.2) / 4,
        "Fats": (calories * 0.25) / 9
    }

def water_intake(weight):
    """Calculate recommended daily water intake in mL."""
    return weight * 35

# App title and configuration
st.set_page_config(page_title="Health & Nutrition Guide", page_icon="🥗", layout="wide")
st.title("Personalized Healthcare & Nutrition App")

# Create two columns for input
col1, col2 = st.columns(2)

# User metrics input
profile = get_profile(conn, st.session_state.user_id)
with col1:
   
    age = profile['age']
    weight = profile['weight']
    height = profile['height']
    
    # Calculate BMI automatically
    bmi = weight / ((height/100)**2)
    bmi_category = "Underweight" if bmi < 18.5 else "Normal weight" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    
    st.metric("Your BMI", f"{bmi:.1f}", bmi_category)
    
    # Diet preferences
    diet_type = st.selectbox("Diet Preference", ["Balanced", "Vegan", "Keto", "Low-Carb", "High-Protein"])
    
    # Mental Health Check-In
    mood = st.select_slider("How do you feel today?", options=["Happy", "Neutral", "Stressed", "Tired"])

# Calculate nutrition needs
total_calories = calculate_calories(age, bmi)
macros = calculate_macros(total_calories)
water = water_intake(weight)

# Display results in second column
with col2:
    st.subheader("Your Daily Nutrition Needs")
    
    # Display calories with progress bar
    st.write(f"*Daily Calories: {total_calories} kcal*")
    st.progress(min(total_calories/3000, 1.0))
    
    # Display macros
    st.write("*Macronutrients Distribution:*")
    col_carbs, col_protein, col_fats = st.columns(3)
    with col_carbs:
        st.metric("Carbs", f"{macros['Carbohydrates']:.0f}g")
    with col_protein:
        st.metric("Protein", f"{macros['Proteins']:.0f}g") 
    with col_fats:
        st.metric("Fats", f"{macros['Fats']:.0f}g")
    
    # Display water intake
    st.write(f"*Water Intake: {water:.0f} mL per day*")
    st.progress(min(water/4000, 1.0))
    
    # Custom recommendations based on mood
    st.subheader("Mood-Based Suggestions")
    if mood == "Stressed":
        st.info("🧘 Try meditation & deep breathing exercises.")
    elif mood == "Tired":
        st.info("💤 Ensure 7-9 hours of quality sleep.")
    else:
        st.success("😊 Keep up the good work!")

# Exercise Recommendations
st.subheader("Exercise Recommendations")
if bmi < 18.5:
    st.write("🔹 Strength training & high-protein diet to gain healthy weight.")
    st.write("🔹 Focus on compound exercises like squats, deadlifts, and bench press.")
elif 18.5 <= bmi <= 24.9:
    st.write("🔹 Balanced mix of strength & cardio workouts.")
    st.write("🔹 Try 3-4 days of strength training and 2-3 days of cardio per week.")
else:
    st.write("🔹 Focus on cardio & weight management exercises.")
    st.write("🔹 Start with low-impact cardio like walking, swimming, or cycling.")

# Personalized meal plan based on diet type
st.subheader(f"Sample {diet_type} Meal Plan")
if diet_type == "Balanced":
    st.write("🍳 *Breakfast*: Oatmeal with fruits and nuts")
    st.write("🥗 *Lunch*: Grilled chicken salad with mixed vegetables")
    st.write("🍲 *Dinner*: Baked salmon with quinoa and steamed vegetables")
elif diet_type == "Vegan":
    st.write("🍳 *Breakfast*: Tofu scramble with vegetables")
    st.write("🥗 *Lunch*: Chickpea and vegetable salad")
    st.write("🍲 *Dinner*: Lentil curry with brown rice")
elif diet_type == "Keto":
    st.write("🍳 *Breakfast*: Eggs with avocado and bacon")
    st.write("🥗 *Lunch*: Tuna salad with olive oil")
    st.write("🍲 *Dinner*: Steak with buttered vegetables")
elif diet_type == "Low-Carb":
    st.write("🍳 *Breakfast*: Greek yogurt with berries")
    st.write("🥗 *Lunch*: Lettuce wrap with turkey and cheese")
    st.write("🍲 *Dinner*: Grilled chicken with vegetables")
elif diet_type == "High-Protein":
    st.write("🍳 *Breakfast*: Protein shake with banana")
    st.write("🥗 *Lunch*: Chicken breast with sweet potato")
    st.write("🍲 *Dinner*: Lean beef stir fry with vegetables")

# Deficiency Risks
st.subheader("Potential Deficiency Risks")
if age > 50:
    st.warning("🛑 Risk of Vitamin D & Calcium deficiency. Include dairy, nuts, and fish.")
elif bmi < 18.5:
    st.warning("🛑 You may lack protein & healthy fats. Add lean meat, eggs, and nuts.")
else:
    st.info("🛑 Maintain a balanced diet to avoid deficiencies.")

# AI Health Chatbot Placeholder
st.subheader("AI Health Chatbot (Coming Soon)")
st.write("💡 Chat with an AI for personalized health advice!")

# Add a disclaimer at the bottom
st.caption("Disclaimer: This app provides general nutrition guidance and is not a substitute for professional medical advice.")