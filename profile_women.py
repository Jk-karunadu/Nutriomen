import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import re
from auth import auth_page
from dashboard import dashboard_page
from profile_page import profile_page
from nutrition_advise import show_nutrition_page

# Page configuration
st.set_page_config(
    page_title="Women's Nutrition Tracker",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize connection to SQLite database
def init_db():
    conn = sqlite3.connect('nutrition_database.db')
    c = conn.cursor()
    
    # Create users table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create profile table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            education TEXT,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            menstruation_date TEXT,
            is_regular_cycle BOOLEAN,
            diseases TEXT,
            food_allergies TEXT,
            is_pregnant BOOLEAN,
            pregnancy_week INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    return conn

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to validate email format
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

# Function to create a new user
def create_user(conn, username, password, email):
    try:
        c = conn.cursor()
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                 (username, hashed_pw, email))
        conn.commit()
        return c.lastrowid  # Return the user ID
    except sqlite3.IntegrityError:
        return None  # User already exists

# Function to verify user credentials
def verify_user(conn, username, password):
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    result = c.fetchone()
    return result[0] if result else None  # Return user ID if found

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

# Initialize database connection
conn = init_db()

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'page' not in st.session_state:
    st.session_state.page = "login"

# Function to handle logout
def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.page = "login"

# Sidebar navigation
if st.session_state.logged_in:
    with st.sidebar:
        st.title("Navigation")
        if st.button("Dashboard"):
            st.session_state.page = "dashboard"
        if st.button("My Profile"):
            st.session_state.page = "profile"
        if st.button("Nutrition Advice"):
            st.session_state.page = "nutrition"
        if st.button("Logout"):
            logout()
            st.experimental_rerun()

# Main application
if not st.session_state.logged_in:
    auth_page(conn)

else:
    # User is logged in - show the appropriate page
    if st.session_state.page == "dashboard":
        dashboard_page(conn)
    
    elif st.session_state.page == "profile":
        profile_page(conn)
    
    elif st.session_state.page == "nutrition":
        show_nutrition_page(conn)

# Close the database connection when the app is done
conn.close()