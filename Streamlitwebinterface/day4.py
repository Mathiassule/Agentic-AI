import streamlit as st
import os
from PIL import Image
from google import genai
from dotenv import load_dotenv

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Agentic OS Dashboard", page_icon="🎛️", layout="wide")
load_dotenv(override=True)

# Initialize the persistent client
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 2. THE SIDEBAR (Control Panel)
# ==========================================
st.sidebar.title("🎛️ Agent OS Controls")
st.sidebar.markdown("Select an active agent below:")

# The selectbox acts as our UI Router
app_mode = st.sidebar.selectbox(
    "Active Tool",
    ["Chat Assistant 💬", "Vision Analyzer 👁️"]
)

st.sidebar.markdown("---")

# Bonus: The Clear Memory Button
if st.sidebar.button("🗑️ Clear Chat Memory"):
    if "messages" in st.session_state:
        del st.session_state.messages
    if "ai_chat" in st.session_state:
        del st.session_state.ai_chat
    st.sidebar.success("Memory wiped!")

# ==========================================
# 3. ROUTER LOGIC: CHAT ASSISTANT
# ==========================================
if app_mode == "Chat Assistant 💬":
    st.title("General Chat Assistant 💬")
    st.markdown("I am your persistent AI memory. What are we working on today?")

    # Initialize memory if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ai_chat" not in st.session_state:
        st.session_state.ai_chat = st.session_state.client.chats.create(model='gemini-2.5-flash-lite')

    # Render history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input and Execution
    prompt = st.chat_input("Message the Assistant...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.ai_chat.send_message(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# 4. ROUTER LOGIC: VISION ANALYZER
# ==========================================
elif app_mode == "Vision Analyzer 👁️":
    st.title("Multimodal Vision Agent 👁️")
    st.markdown("Upload an image. I will extract text, identify objects, and analyze the scene.")

    uploaded_file = st.file_uploader("Drag and drop an image here...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Display the image in a smaller column so it doesn't take up the whole screen
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
        with col2:
            user_prompt = st.text_input("Prompt:", value="Describe this image in detail.")
            
            if st.button("Run Analysis", type="primary"):
                with st.spinner("Analyzing pixels..."):
                    try:
                        response = st.session_state.client.models.generate_content(
                            model='gemini-2.5-flash-lite',
                            contents=[user_prompt, image]
                        )
                        st.success("Analysis Complete!")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Error: {e}")