import streamlit as st
import sqlite3
import hashlib
import re
from datetime import datetime

# Initialize connection to SQLite database
def init_db():
    conn = sqlite3.connect('user_database.db')
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        return True
    except sqlite3.IntegrityError:
        # This will happen if username or email already exists
        return False

# Function to verify user credentials
def verify_user(conn, username, password):
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    result = c.fetchone()
    return result is not None

# Page configuration
st.set_page_config(page_title="Login & Signup System", page_icon="🔐", layout="centered")

# Initialize database connection
conn = init_db()

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Function to handle login
def login():
    st.session_state.logged_in = verify_user(conn, username, password)
    if st.session_state.logged_in:
        st.session_state.username = username

# Function to handle logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# Main application
if st.session_state.logged_in:
    # User is logged in - show the application content
    st.title(f"Welcome, {st.session_state.username}! 👋")
    
    st.write("You are now logged into the application. This is where your main app content would go.")
    
    # Example of app content
    st.subheader("Application Dashboard")
    st.write("Here's some example content for your application:")
    
    # Sample metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
    with col2:
        st.metric(label="Wind", value="9 mph", delta="-8%")
    with col3:
        st.metric(label="Humidity", value="86%", delta="4%")
    
    # Logout button at bottom
    if st.button("Logout"):
        logout()
        st.experimental_rerun()

else:
    # User is not logged in - show login/signup form
    st.title("Authentication System 🔐")
    
    # Create tabs for Login and Signup
    tab1, tab2 = st.tabs(["Login", "Signup"])
    
    # Login Tab
    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            login_btn = st.button("Login")
        
        if login_btn:
            if username and password:
                if verify_user(conn, username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    # Signup Tab
    with tab2:
        st.header("Create New Account")
        new_username = st.text_input("Username", key="signup_username")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            signup_btn = st.button("Signup")
        
        if signup_btn:
            if not new_username or not new_email or not new_password:
                st.warning("Please fill out all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            elif not is_valid_email(new_email):
                st.error("Please enter a valid email address")
            else:
                if create_user(conn, new_username, new_password, new_email):
                    st.success("Account created successfully! You can now login.")
                else:
                    st.error("Username or email already exists")

# Close the database connection when the app is done
conn.close()