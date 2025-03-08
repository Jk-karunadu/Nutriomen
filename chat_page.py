import streamlit as st
import openai

# Set up OpenAI API
openai.api_key = "your_api_key_here"

# Title
st.title("🥗 AI-Powered Nutrition Chatbot for Women")

# Sidebar - User Information
st.sidebar.header("👩 User Information")
age = st.sidebar.number_input("Age", min_value=12, max_value=100, value=25)
diet_preference = st.sidebar.selectbox("Diet Preference", ["Vegetarian", "Vegan", "Non-Vegetarian", "Keto", "Other"])
goal = st.sidebar.selectbox("Health Goal", ["Weight Loss", "Muscle Gain", "General Health", "Pregnancy Nutrition"])

# Chatbot
st.subheader("🤖 Chat with your AI Nutritionist")
chat_history = st.session_state.get("chat_history", [])

# Display previous chat history
for message in chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input field
user_input = st.chat_input("Ask me anything about nutrition...")

if user_input:
    # Append user input to chat history
    chat_history.append({"role": "user", "content": user_input})

    # AI Response
    prompt = f"You are a nutritionist guiding a {age}-year-old {diet_preference} woman whose goal is {goal}. {user_input}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert nutritionist giving diet advice for women."},
                  {"role": "user", "content": prompt}]
    )

    bot_reply = response["choices"][0]["message"]["content"]

    # Append bot response to chat history
    chat_history.append({"role": "assistant", "content": bot_reply})

    # Store chat history in session state
    st.session_state.chat_history = chat_history

    # Display bot response
    with st.chat_message("assistant"):
        st.write(bot_reply)