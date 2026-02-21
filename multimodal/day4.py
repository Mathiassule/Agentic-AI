import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from colorama import init, Fore

# Initialize
init(autoreset=True)
load_dotenv()

# ==========================================
# 1. SETUP CLIENT
# ==========================================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_video(video_path):
    print(Fore.CYAN + f"🎥 Preparing to upload video: {video_path}...")
    
    try:
        # 2. UPLOAD FILE TO GENAI STORAGE
        # Large files (videos) are best handled via the File API, not raw bytes.
        video_file = client.files.upload(file=video_path)
        
        print(Fore.YELLOW + f"✔ Upload complete: {video_file.name}")
        print(Fore.YELLOW + "⏳ Waiting for video processing (this takes a few seconds)...")

        # 3. WAIT FOR PROCESSING
        # The API needs time to process the video before inference.
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            print(Fore.RED + "\n❌ Video processing failed.")
            return

        print(Fore.GREEN + "\n✔ Video is ready for analysis!")

        # 4. GENERATE CONTENT
        # We pass the file object (URI) to the model.
        prompt = "Watch this video carefully. Describe the main action, the setting, and any audio you hear."
        
        print(Fore.MAGENTA + "🤖 Analyzing video content...")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[prompt, video_file]
        )
        
        print(Fore.WHITE + "\nAnalysis Result:")
        print(response.text)
        
        # 5. CLEANUP (Optional but good practice)
        # client.files.delete(name=video_file.name) 

    except FileNotFoundError:
        print(Fore.RED + "Error: Video file not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # TASK: Record a short video and name it 'video.mp4'
    my_video = "video.mp4"
    
    if not os.path.exists(my_video):
        print(Fore.RED + f"⚠ Please place a video file named '{my_video}' in this folder.")
    else:
        analyze_video(my_video)