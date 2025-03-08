import streamlit as st
from PIL import Image
import pandas as pd
import random
import base64

# Set page configuration
st.set_page_config(
    page_title="NourishHer - Nutrition for Every Stage",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
        .main {
            background-color: #fff9f9;
        }
        .stApp {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        h1, h2, h3 {
            color: #ff6b6b;
        }
        .quote-container {
            background: linear-gradient(135deg, #ff6b6b, #ff9a8b);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 10px 0;
        }
        .quote-text {
            font-style: italic;
            font-size: 1.2em;
        }
        .quote-author {
            font-weight: bold;
            margin-top: 10px;
        }
        .feature-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin: 10px 0;
            text-align: center;
            height: 100%;
        }
        .centered {
            text-align: center;
        }
        .button-style {
            background-color: #4ecdc4;
            color: white;
            padding: 0.5em 1em;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }
        .stButton>button {
            background-color: #4ecdc4;
            color: white;
            font-weight: bold;
            border-radius: 50px;
            border: none;
            padding: 0.5em 2em;
        }
        .stTextInput>div>div>input {
            border-radius: 50px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Sidebar content
with st.sidebar:
    st.title("NourishHer 🌿")
    st.markdown("### Your Nutrition Journey")
    
    # Navigation options
    st.header("Navigation")
    nav_options = ["Home", "Personalized Plan", "Life Stages", "Recipes", "Community", "About Us"]
    selected_nav = st.radio("", nav_options)
    
    st.header("Quick Health Check")
    age = st.number_input("Age", min_value=10, max_value=100, value=30)
    
    life_stage = st.selectbox(
        "Life Stage",
        ["Adolescence", "Adult", "Pregnancy", "Postpartum", "Perimenopause", "Menopause", "Post-menopause"]
    )
    
    health_goals = st.multiselect(
        "Health Goals",
        ["Weight Management", "Energy Boost", "Hormonal Balance", "Bone Health", "Heart Health", "Mental Wellness"]
    )
    
    if st.button("Get Started"):
        st.success("Your profile has been created! Explore the app to find personalized nutrition advice.")

# Main content - Home page
def home():
    # Hero section
    st.markdown("<h1 class='centered'>Nutrition Personalized for Every Stage of Womanhood</h1>", unsafe_allow_html=True)
    st.markdown("<p class='centered'>From puberty to pregnancy, motherhood to menopause — we're here to support your unique nutritional needs at every step of your journey.</p>", unsafe_allow_html=True)
    
    # Placeholder for hero image - you would replace this with a real image
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        st.image("https://via.placeholder.com/800x400?text=Women+at+Different+Life+Stages", use_column_width=True)
    
    # Motivational quote carousel
    st.markdown("<h2 class='centered'>Words That Inspire</h2>", unsafe_allow_html=True)
    
    quotes = [
        {"text": "The food you eat can be either the safest and most powerful form of medicine or the slowest form of poison.", "author": "Ann Wigmore"},
        {"text": "Your body is a temple, but only if you treat it as one.", "author": "Astrid Alauda"},
        {"text": "Take care of your body. It's the only place you have to live.", "author": "Jim Rohn"},
        {"text": "Nourishing yourself in a way that helps you blossom in the direction you want to go is attainable, and you are worth the effort.", "author": "Deborah Day"},
        {"text": "The greatest wealth is health.", "author": "Virgil"},
        {"text": "The journey of a thousand miles begins with a single step.", "author": "Lao Tzu"},
        {"text": "A woman is the full circle. Within her is the power to create, nurture and transform.", "author": "Diane Mariechild"}
    ]
    
    # Display random quote
    quote = random.choice(quotes)
    st.markdown(f"""
    <div class="quote-container">
        <div class="quote-text">"{quote['text']}"</div>
        <div class="quote-author">— {quote['author']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Show Another Quote"):
        st.experimental_rerun()
    
    # Features section
    st.markdown("<h2 class='centered'>How We Support You</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>Personalized Nutrition</h3>
            <p>Get customized meal plans and nutrition advice based on your life stage, health goals, and unique needs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>Expert Guidance</h3>
            <p>Connect with registered dietitians and women's health specialists for evidence-based recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>Delicious Recipes</h3>
            <p>Access hundreds of nutrient-dense recipes designed specifically for women's health needs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>Supportive Community</h3>
            <p>Join thousands of women sharing their health journeys, challenges, and victories.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Start your journey section
    st.markdown("<h2 class='centered'>Start Your Health Journey Today</h2>", unsafe_allow_html=True)
    
    with st.form("user_details_form"):
        st.markdown("<p class='centered'>Enter your details to get personalized nutrition recommendations</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
            age = st.number_input("Age", min_value=10, max_value=100, value=30)
        
        with col2:
            height = st.number_input("Height (cm)", min_value=100, max_value=220, value=165)
            weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=60)
            activity_level = st.select_slider(
                "Activity Level",
                options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"]
            )
        
        life_stage = st.selectbox(
            "Life Stage",
            ["Adolescence", "Adult", "Pregnancy", "Postpartum", "Perimenopause", "Menopause", "Post-menopause"]
        )
        
        submitted = st.form_submit_button("Create My Plan")
        if submitted:
            st.success("Thank you for submitting your information! Your personalized nutrition plan is being created.")
    
    # Testimonials
    st.markdown("<h2 class='centered'>Stories from Our Community</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <p>"This program helped me navigate the nutritional challenges of pregnancy. I've never felt healthier or more energetic!"</p>
            <p>— Sarah, 32, Expectant Mother</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <p>"The personalized approach to menopause nutrition has been life-changing. My symptoms have significantly reduced."</p>
            <p>— Linda, 51, Business Owner</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <p>"As a college athlete, I needed specific nutrition guidance. This platform delivered exactly what I needed to perform my best."</p>
            <p>— Maya, 20, Student Athlete</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025 NourishHer. All rights reserved.</p>
        <p>Created with ❤ for women's health and nutrition</p>
    </div>
    """, unsafe_allow_html=True)

# Route to the correct page based on navigation
if selected_nav == "Home":
    home()
else:
    st.title(f"{selected_nav} Page")
    st.write("This section is under development for the hackathon.")
    st.info(f"The {selected_nav} feature will include specialized content related to women's nutrition needs.")

# Add a decorative element at the bottom
st.markdown("""
<div style="text-align: center; margin-top: 30px;">
    <p>🌿 🍎 🥗 🍓 🥑 🍒 🥦 🍇</p>
</div>
""", unsafe_allow_html=True)