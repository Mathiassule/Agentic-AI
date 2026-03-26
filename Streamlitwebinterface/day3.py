import streamlit as st
import os
from google import genai
from dotenv import load_dotenv

# ==========================================
# 1. SETUP
# ==========================================
st.set_page_config(page_title="Agent with Memory", page_icon="🧠")

load_dotenv(override=True)

st.title("The Agent with a Memory 🧠")
st.markdown("Unlike Day 1, this chat remembers what you said 5 minutes ago!")

# ==========================================
# 2. STATE MANAGEMENT (The "Brain")
# ==========================================
# A. Save the CLIENT to memory so it doesn't close on rerun
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# B. Save the UI history
if "messages" not in st.session_state:
    st.session_state.messages = []

# C. Create the chat using the saved client
if "ai_chat" not in st.session_state:
    st.session_state.ai_chat = st.session_state.client.chats.create(model='gemini-2.5-flash-lite')

# ==========================================
# 3. RENDER THE HISTORY
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 4. CHAT INPUT & EXECUTION
# ==========================================
prompt = st.chat_input("Say something...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Use the stateful chat object
                response = st.session_state.ai_chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Error: {e}")