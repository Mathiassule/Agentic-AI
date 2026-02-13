import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from colorama import init, Fore

# Initialize
init(autoreset=True)
load_dotenv()

# ==========================================
# 1. SETUP CLIENT (New SDK)
# ==========================================
# Instead of genai.configure, we instantiate a Client.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(image_path):
    print(Fore.CYAN + f"📸 Loading image: {image_path}...")
    
    try:
        # 2. LOAD IMAGE
        # The new SDK handles PIL images directly in the 'contents' list.
        image = Image.open(image_path)
        
        prompt_text = "Describe what is happening in this image in technical detail."

        print(Fore.YELLOW + "🤖 Analyzing visual data with Gemini 2.5 Flash Lite...")
        
        # 3. GENERATE (Streaming)
        # We use the 'contents' parameter which can take a mix of text and images.
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash-lite',
            contents=[prompt_text, image]
        )
        
        print(Fore.GREEN + "\nDescription:")
        for chunk in response:
            # In the new SDK, we access .text usually, but check for None chunks
            if chunk.text:
                print(Fore.WHITE + chunk.text, end="", flush=True)
            
    except FileNotFoundError:
        print(Fore.RED + "Error: Image file not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # Ensure you have a 'test_image.jpg' in your folder!
    my_image = "test_image.jpg"
    
    if not os.path.exists(my_image):
        print(Fore.RED + f"⚠ Please place an image named '{my_image}' in this folder.")
    else:
        analyze_image(my_image)