import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()

# ==========================================
# 1. SETUP CLIENT (New SDK)
# ==========================================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def compare_images(path_a, path_b):
    print(Fore.CYAN + f"📸 Loading images: {path_a} and {path_b}...")
    
    try:
        # 2. LOAD IMAGES
        img1 = Image.open(path_a)
        img2 = Image.open(path_b)
        
        # 3. CONSTRUCT MULTIMODAL PROMPT
        # We pass both image objects into the contents list.
        # The order matters! The model sees them in the order provided.
        prompt_text = """
        Compare Image 1 and Image 2.
        1. List the key similarities.
        2. List the key differences.
        3. What is the relationship between them? (e.g., before/after, zoom in, different angles).
        """
        
        print(Fore.YELLOW + "🤖 Analyzing visual relationship with Gemini 2.5 Flash Lite...")
        
        # 4. GENERATE CONTENT
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[prompt_text, img1, img2]
        )
        
        print(Fore.GREEN + "\nAnalysis Report:")
        print(Style.DIM + "------------------------------------------------")
        if response.text:
            print(Fore.WHITE + response.text)
        print(Style.DIM + "------------------------------------------------")

    except FileNotFoundError:
        print(Fore.RED + "Error: One or both image files not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # TASK: Find two images.
    # Idea: Take a photo of your desk. Move a cup. Take another photo.
    file_1 = "image_a.jpg"
    file_2 = "image_b.jpg"
    
    # Check if files exist to avoid crash
    if not os.path.exists(file_1) or not os.path.exists(file_2):
        print(Fore.RED + f"⚠ Please place '{file_1}' and '{file_2}' in this folder.")
    else:
        compare_images(file_1, file_2)