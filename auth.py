import streamlit as st
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import re

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

def auth_page(conn):
    st.title("Women's Nutrition Tracker 🌿")
    st.write("Track your nutrition needs based on your specific profile")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # Login Tab
    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            if username and password:
                user_id = verify_user(conn, username, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.session_state.page = "dashboard"
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

        if st.button("Signup", key="signup_btn"):
            if not new_username or not new_email or not new_password:
                st.warning("Please fill out all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            elif not is_valid_email(new_email):
                st.error("Please enter a valid email address")
            else:
                user_id = create_user(conn, new_username, new_password, new_email)
                if user_id:
                    st.success("Account created successfully! You can now login.")
                else:
                    st.error("Username or email already exists")
