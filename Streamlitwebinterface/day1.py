import streamlit as st
import os
from google import genai
from dotenv import load_dotenv

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
# Set the page title and icon
st.set_page_config(page_title="Agentic Chat", page_icon="🤖")

# Load environment variables (API Key)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 2. UI HEADER
# ==========================================
st.title("My First AI Web App 🚀")
st.markdown("Welcome to the visual interface for our Gemini Agent. Type a message below!")

# ==========================================
# 3. CHAT INTERFACE
# ==========================================
# st.chat_input creates the text box at the bottom of the screen
prompt = st.chat_input("Ask the agent something...")

if prompt:
    # 1. Display the user's message on the screen
    with st.chat_message("user"):
        st.write(prompt)
        
    # 2. Display a loading spinner while the AI thinks
    with st.spinner("Agent is thinking..."):
        try:
            # Call the Google GenAI SDK
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            
            # 3. Display the AI's response on the screen
            with st.chat_message("assistant"):
                st.write(response.text)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")