import streamlit as st
from datetime import datetime
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize LLM helper
class LLMHelper:
    """Helper class to interact with ChatGroq's Llama3 model."""
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-8b-8192"
        )
    
    def get_response(self, prompt):
        """Send the prompt to ChatGroq and return the response."""
        response = self.llm.invoke(prompt)
        return response.content  # Extract and return the response content
    


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


def get_profile(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    
    if result:
        columns = [desc[0] for desc in c.description]
        profile = {columns[i]: result[i] for i in range(len(columns))}
        return profile
    return None


def show_nutrition_page(conn):
    st.title("Personalized Nutrition Advice")
    
    # Initialize LLM helper
    llm_helper = LLMHelper()
    
    # Get user profile
    profile = get_profile(conn, st.session_state.user_id)
    
    if not profile:
        st.warning("Please complete your profile first to get personalized advice.")
        if st.button("Go to Profile"):
            st.session_state.page = "profile"
            st.experimental_rerun()
    else:
        col1, col2 = st.columns(2)

# User metrics input

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
        
        # Calculate BMI
        bmi = profile['weight'] / ((profile['height']/100) ** 2)
        
        # Display basic metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Age", f"{profile['age']} years")
            st.metric("Weight", f"{profile['weight']} kg")
            st.metric("Height", f"{profile['height']} cm")
        with col2:
            st.metric("BMI", f"{bmi:.1f}")
            if profile['is_pregnant']:
                st.metric("Pregnancy Status", f"Week {profile['pregnancy_week']}")
            else:
                days_since_period = (datetime.now() - datetime.strptime(profile['menstruation_date'], '%Y-%m-%d')).days
                st.metric("Days Since Last Period", days_since_period)
        
        # Nutrition recommendations based on profile
        st.subheader("Recommended Daily Nutrition")
        
        # Base calorie needs (simplified calculation)
        base_calories = 655 + (9.6 * profile['weight']) + (1.8 * profile['height']) - (4.7 * profile['age'])
        
        # Adjust for activity level
        activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        
        activity_multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725
        }
        
        adjusted_calories = base_calories * activity_multipliers[activity_level]
        
        # Adjust for pregnancy if applicable
        if profile['is_pregnant']:
            if profile['pregnancy_week'] <= 13:
                adjusted_calories += 0  
            elif profile['pregnancy_week'] <= 26:
                adjusted_calories += 340
            else:
                adjusted_calories += 450
        
        st.write(f"**Estimated Daily Caloric Needs:** {adjusted_calories:.0f} calories")
        
        # Macronutrient breakdown
        st.subheader("Macronutrient Distribution")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            protein_percent = 20
            protein_cals = adjusted_calories * (protein_percent/100)
            protein_grams = protein_cals / 4
            st.metric("Protein", f"{protein_grams:.0f}g", f"{protein_percent}%")
        
        with col2:
            carb_percent = 50
            carb_cals = adjusted_calories * (carb_percent/100)
            carb_grams = carb_cals / 4
            st.metric("Carbohydrates", f"{carb_grams:.0f}g", f"{carb_percent}%")
        
        with col3:
            fat_percent = 30
            fat_cals = adjusted_calories * (fat_percent/100)
            fat_grams = fat_cals / 9
            st.metric("Fats", f"{fat_grams:.0f}g", f"{fat_percent}%")
        
        # Special considerations based on profile
        st.subheader("Special Considerations")
        
        recommendations = []
        
        # Age-based recommendations
        if profile['age'] < 30:
            recommendations.append("**Young Adult:** Focus on building bone density with calcium-rich foods.")
        elif profile['age'] < 50:
            recommendations.append("**Adult:** Maintain muscle mass with adequate protein and regular exercise.")
        else:
            recommendations.append("**50+:** Increase calcium and vitamin D for bone health. Consider B12 supplements.")
        
        # Menstrual cycle recommendations
        if not profile['is_pregnant']:
            days_since_period = (datetime.now() - datetime.strptime(profile['menstruation_date'], '%Y-%m-%d')).days
            if days_since_period < 7:
                recommendations.append("**During Menstruation:** Increase iron-rich foods to replace lost iron. Stay hydrated.")
            
            if not profile['is_regular_cycle']:
                recommendations.append("**Irregular Cycle:** Consider omega-3 fatty acids and vitamin E to support hormonal balance.")
        
        # Pregnancy recommendations
        if profile['is_pregnant']:
            recommendations.append("**Pregnancy:** Essential nutrients include folic acid, iron, calcium, and DHA.")
            if profile['pregnancy_week'] <= 13:
                recommendations.append("**First Trimester:** Focus on small, frequent meals if experiencing nausea.")
            elif profile['pregnancy_week'] <= 26:
                recommendations.append("**Second Trimester:** Increase calcium intake for baby's bone development.")
            else:
                recommendations.append("**Third Trimester:** Include more fiber and water to prevent constipation.")
        
        # BMI-based recommendations
        if bmi < 18.5:
            recommendations.append("**Underweight:** Focus on nutrient-dense foods to reach a healthy weight.")
        elif bmi >= 25 and bmi < 30:
            recommendations.append("**Overweight:** Consider balanced portion control while maintaining nutrient intake.")
        elif bmi >= 30:
            recommendations.append("**Obesity Range:** Focus on whole foods and consider consulting with a dietitian.")
        
        # Medical conditions
        if profile['diseases']:
            recommendations.append(f"**Medical Considerations:** Your conditions ({profile['diseases']}) may require specific dietary adjustments. Consult with a healthcare provider.")
        
        # Food allergies
        if profile['food_allergies']:
            recommendations.append(f"**Food Allergies/Intolerances:** Find alternative sources for nutrients typically found in {profile['food_allergies']}.")
        
        for rec in recommendations:
            st.write(rec)
        
        st.write("---")
        
        # LLM-enhanced personalized advice section
        st.subheader("Personalized Advice")
        
        if 'advice_generated' not in st.session_state:
            st.session_state.advice_generated = False
            
        if not st.session_state.advice_generated:
            # Create a prompt based on user profile
            prompt = f"""
            Generate personalized nutrition advice for a {profile['age']}-year-old individual with the following characteristics:
            - Weight: {profile['weight']} kg
            - Height: {profile['height']} cm
            - BMI: {bmi:.1f}
            - Activity level: {activity_level}
            """
            
            if profile['is_pregnant']:
                prompt += f"- Currently pregnant (Week {profile['pregnancy_week']})\n"
            else:
                prompt += f"- Last menstrual period: {profile['menstruation_date']}\n"
                prompt += f"- Regular menstrual cycle: {'Yes' if profile['is_regular_cycle'] else 'No'}\n"
            
            if profile['diseases']:
                prompt += f"- Medical conditions: {profile['diseases']}\n"
            
            if profile['food_allergies']:
                prompt += f"- Food allergies/intolerances: {profile['food_allergies']}\n"
                
            prompt += """
            Please provide:
            1. Three specific meal suggestions for breakfast, lunch, and dinner
            2. Two healthy snack options
            3. Any specific nutrients they should focus on based on their profile
            4. Brief lifestyle recommendations
            
            Keep the advice concise, practical, and evidence-based with attractive emojis.
            """
            
            with st.spinner("Generating personalized advice..."):
                try:
                    llm_response = llm_helper.get_response(prompt)
                    st.session_state.llm_advice = llm_response
                    st.session_state.advice_generated = True
                except Exception as e:
                    st.error(f"Error generating advice: {str(e)}")
        
        if st.session_state.advice_generated:
            st.markdown(st.session_state.llm_advice)
            if st.button("Regenerate Advice"):
                st.session_state.advice_generated = False
                st.experimental_rerun()

        
        st.title("Nutrition Assistant Chat")
    
    # Initialize LLM helper
    llm_helper = LLMHelper()
    
    # Get user profile
    profile = get_profile(conn, st.session_state.user_id)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
    
    # Chat input
    user_query = st.chat_input("Ask about nutrition, health, or your personalized plan...")
    
    if user_query:
        # Display user message
        st.chat_message("user").write(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Prepare context for the LLM
        context = ""
        if profile:
            context = f"""
            User profile:
            - Age: {profile['age']} years
            - Weight: {profile['weight']} kg
            - Height: {profile['height']} cm
            - BMI: {profile['weight'] / ((profile['height']/100) ** 2):.1f}
            """
           
            
            if profile['is_pregnant']:
                context += f"- Currently pregnant (Week {profile['pregnancy_week']})\n"
            
            if profile['diseases']:
                context += f"- Medical conditions: {profile['diseases']}\n"
            
            if profile['food_allergies']:
                context += f"- Food allergies/intolerances: {profile['food_allergies']}\n"
            context += user_query
        # Create a prompt with context and chat history
        prompt = f"""
        You are a nutrition assistant helping a user with personalized health and nutrition advice.
        
        {context}
        
        Previous conversation:
        """
        
        # Add abbreviated chat history (last 5 messages)
        history_subset = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history
        for msg in history_subset[:-1]:  # Exclude the latest user message which we'll add separately
            prompt += f"\n{msg['role'].upper()}: {msg['content']}"
        
        # Add the current query
        prompt += f"\n\nUser's current question: {user_query}\n\nProvide a helpful, accurate, and concise response:"
        
        # Get response from LLM
        with st.spinner("Thinking..."):
            try:
                llm_response = llm_helper.get_response(prompt)
                
                # Display assistant response
                st.chat_message("assistant").write(llm_response)
                st.session_state.chat_history.append({"role": "assistant", "content": llm_response})
            except Exception as e:
                error_message = f"I'm sorry, I couldn't process your request. Error: {str(e)}"
                st.chat_message("assistant").write(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})

        st.write("---")
        st.write("**Note:** These recommendations are general guidelines. Please consult with a healthcare provider or registered dietitian for personalized advice.")


def show_chat_page(conn):
    st.title("Nutrition Assistant Chat")
    
    # Initialize LLM helper
    llm_helper = LLMHelper()
    
    # Get user profile
    profile = get_profile(conn, st.session_state.user_id)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
    
    # Chat input
    user_query = st.chat_input("Ask about nutrition, health, or your personalized plan...")
    
    if user_query:
        # Display user message
        st.chat_message("user").write(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Prepare context for the LLM
        context = ""
        if profile:
            context = f"""
            User profile:
            - Age: {profile['age']} years
            - Weight: {profile['weight']} kg
            - Height: {profile['height']} cm
            - BMI: {profile['weight'] / ((profile['height']/100) ** 2):.1f}
            """
            
            if profile['is_pregnant']:
                context += f"- Currently pregnant (Week {profile['pregnancy_week']})\n"
            
            if profile['diseases']:
                context += f"- Medical conditions: {profile['diseases']}\n"
            
            if profile['food_allergies']:
                context += f"- Food allergies/intolerances: {profile['food_allergies']}\n"
        
        # Create a prompt with context and chat history
        prompt = f"""
        You are a nutrition assistant helping a user with personalized health and nutrition advice.
        
        {context}
        
        Previous conversation:
        """
        
        # Add abbreviated chat history (last 5 messages)
        history_subset = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history
        for msg in history_subset[:-1]:  # Exclude the latest user message which we'll add separately
            prompt += f"\n{msg['role'].upper()}: {msg['content']}"
        
        # Add the current query
        prompt += f"\n\nUser's current question: {user_query}\n\nProvide a helpful, accurate, and concise response:"
        
        # Get response from LLM
        with st.spinner("Thinking..."):
            try:
                llm_response = llm_helper.get_response(prompt)
                
                # Display assistant response
                st.chat_message("assistant").write(llm_response)
                st.session_state.chat_history.append({"role": "assistant", "content": llm_response})
            except Exception as e:
                error_message = f"I'm sorry, I couldn't process your request. Error: {str(e)}"
                st.chat_message("assistant").write(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})