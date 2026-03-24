import streamlit as st
import os
from PIL import Image
from google import genai
from dotenv import load_dotenv

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Vision Agent", page_icon="👁️")

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 2. UI HEADER
# ==========================================
st.title("Multimodal Vision Agent 📸")
st.markdown("Upload any image below and ask the AI to analyze its contents.")

# ==========================================
# 3. THE DRAG-AND-DROP UPLOADER
# ==========================================
# Streamlit handles all the complex HTML/JS for file uploading automatically
uploaded_file = st.file_uploader("Drag and drop an image here...", type=["jpg", "jpeg", "png", "webp"])

# Only run the rest of the code IF a file has been uploaded
if uploaded_file is not None:
    
    # Open the file using PIL (Python Imaging Library)
    image = Image.open(uploaded_file)
    
    # Display a preview of the uploaded image on the web page
    st.image(image, caption="Ready for analysis.", use_container_width=True)
    
    # ==========================================
    # 4. INTERACTION
    # ==========================================
    # Provide a default prompt, but let the user change it
    user_prompt = st.text_input(
        "What do you want to know about this image?", 
        value="Extract all the text and describe the main objects."
    )
    
    # A button to trigger the API call (prevents it from running on every keystroke)
    if st.button("Analyze Image"):
        
        with st.spinner("Analyzing pixels..."):
            try:
                # Pass BOTH the text prompt and the PIL image object
                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=[user_prompt, image]
                )
                
                # Display the results in a nice green success box
                st.success("Analysis Complete!")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")