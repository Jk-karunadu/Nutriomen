import streamlit as st

from datetime import datetime

# Function to save user profile
def save_profile(conn, profile_data):
    try:
        c = conn.cursor()
        
        # Check if profile already exists
        c.execute("SELECT id FROM profiles WHERE user_id = ?", (profile_data['user_id'],))
        existing_profile = c.fetchone()
        
        if existing_profile:
            # Update existing profile
            query = '''
            UPDATE profiles SET 
                full_name = ?, age = ?, education = ?, height = ?, weight = ?,
                menstruation_date = ?, is_regular_cycle = ?, diseases = ?,
                food_allergies = ?, is_pregnant = ?, pregnancy_week = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
            '''
            c.execute(query, (
                profile_data['full_name'], profile_data['age'], profile_data['education'],
                profile_data['height'], profile_data['weight'], profile_data['menstruation_date'],
                profile_data['is_regular_cycle'], profile_data['diseases'], profile_data['food_allergies'],
                profile_data['is_pregnant'], profile_data['pregnancy_week'], profile_data['user_id']
            ))
        else:
            # Insert new profile
            query = '''
            INSERT INTO profiles (
                user_id, full_name, age, education, height, weight,
                menstruation_date, is_regular_cycle, diseases,
                food_allergies, is_pregnant, pregnancy_week
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            c.execute(query, (
                profile_data['user_id'], profile_data['full_name'], profile_data['age'], 
                profile_data['education'], profile_data['height'], profile_data['weight'],
                profile_data['menstruation_date'], profile_data['is_regular_cycle'], 
                profile_data['diseases'], profile_data['food_allergies'],
                profile_data['is_pregnant'], profile_data['pregnancy_week']
            ))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

# Function to get user profile
def get_profile(conn, user_id):
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    
    if result:
        columns = [desc[0] for desc in c.description]
        profile = {columns[i]: result[i] for i in range(len(columns))}
        return profile
    return None

def profile_page(conn):
    st.title("My Nutrition Profile")
    st.write("Please provide your details for personalized nutrition recommendations.")

    # Get existing profile if available
    existing_profile = get_profile(conn, st.session_state.user_id)

    # Create form for profile information
    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name", value=existing_profile['full_name'] if existing_profile else "")
            age = st.number_input("Age", min_value=18, max_value=100, value=existing_profile['age'] if existing_profile else 25)
            education = st.selectbox("Education Level", 
                                    ["High School", "Bachelor's", "Master's", "PhD", "Other"],
                                    index=["High School", "Bachelor's", "Master's", "PhD", "Other"].index(existing_profile['education']) if existing_profile and existing_profile['education'] in ["High School", "Bachelor's", "Master's", "PhD", "Other"] else 0)
            height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=float(existing_profile['height']) if existing_profile else 165.0)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=float(existing_profile['weight']) if existing_profile else 60.0)

        with col2:
            menstruation_date = st.date_input("Last Menstruation Start Date", 
                                              value=datetime.strptime(existing_profile['menstruation_date'], '%Y-%m-%d').date() if existing_profile and existing_profile['menstruation_date'] else datetime.now().date())
            is_regular_cycle = st.checkbox("Regular Menstrual Cycle", value=bool(existing_profile['is_regular_cycle']) if existing_profile else True)
            diseases = st.text_area("Medical Conditions (if any)", value=existing_profile['diseases'] if existing_profile else "")
            food_allergies = st.text_area("Food Allergies/Intolerances", value=existing_profile['food_allergies'] if existing_profile else "")
            is_pregnant = st.checkbox("Currently Pregnant", value=bool(existing_profile['is_pregnant']) if existing_profile else False)

            pregnancy_week = st.slider("Pregnancy Week", 1, 42, value=existing_profile['pregnancy_week'] if existing_profile and existing_profile['is_pregnant'] else 1) if is_pregnant else 0

        submit = st.form_submit_button("Save Profile")

        if submit:
            profile_data = {
                'user_id': st.session_state.user_id,
                'full_name': full_name,
                'age': age,
                'education': education,
                'height': height,
                'weight': weight,
                'menstruation_date': menstruation_date.strftime('%Y-%m-%d'),
                'is_regular_cycle': is_regular_cycle,
                'diseases': diseases,
                'food_allergies': food_allergies,
                'is_pregnant': is_pregnant,
                'pregnancy_week': pregnancy_week
            }

            if save_profile(conn, profile_data):
                st.success("Profile saved successfully!")
                st.session_state.page = "dashboard"
                st.experimental_rerun()
