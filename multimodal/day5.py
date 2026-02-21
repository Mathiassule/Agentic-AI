import os
import shutil
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from PIL import Image
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()

# ==========================================
# 1. DEFINE THE METADATA SCHEMA
# ==========================================
class ImageMetadata(BaseModel):
    suggested_filename: str = Field(description="A descriptive filename using snake_case (e.g., 'dog_running_park'). Do not include extension.")
    category: str = Field(description="One of: 'Documents', 'People', 'Nature', 'Tech', 'Misc'")
    description: str = Field(description="A short 1-sentence caption of the image.")

# ==========================================
# 2. THE SMART GALLERY AGENT
# ==========================================
class SmartGalleryAgent:
    def __init__(self, target_folder):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.target_folder = target_folder
        self.supported_exts = {'.jpg', '.jpeg', '.png', '.webp'}

    def analyze_image(self, file_path):
        """Sends image to Gemini to get metadata."""
        print(Fore.CYAN + f"👀 Analyzing: {os.path.basename(file_path)}...")
        
        try:
            image = Image.open(file_path)
            
            prompt = "Analyze this image. Generate a descriptive filename and categorize it."
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=ImageMetadata
                )
            )
            
            if response.text:
                return ImageMetadata(**json.loads(response.text))
            return None

        except Exception as e:
            print(Fore.RED + f"❌ Error analyzing image: {e}")
            return None

    def organize(self):
        """Main loop to scan and rename files."""
        if not os.path.exists(self.target_folder):
            print(Fore.RED + f"Folder '{self.target_folder}' does not exist.")
            return

        files = [f for f in os.listdir(self.target_folder) if os.path.isfile(os.path.join(self.target_folder, f))]
        
        print(Fore.YELLOW + f"📂 Found {len(files)} files in '{self.target_folder}'\n")

        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext.lower() not in self.supported_exts:
                continue

            old_path = os.path.join(self.target_folder, filename)
            
            # 1. GET METADATA
            metadata = self.analyze_image(old_path)
            
            if metadata:
                # 2. CONSTRUCT NEW PATH
                # Create category subfolder (e.g., my_gallery/Nature)
                category_folder = os.path.join(self.target_folder, metadata.category)
                os.makedirs(category_folder, exist_ok=True)
                
                # Create new filename (e.g., dog_park.jpg)
                new_filename = f"{metadata.suggested_filename}{ext.lower()}"
                new_path = os.path.join(category_folder, new_filename)
                
                # Handle duplicates (simple check)
                if os.path.exists(new_path):
                    new_filename = f"{metadata.suggested_filename}_v2{ext.lower()}"
                    new_path = os.path.join(category_folder, new_filename)

                # 3. RENAME & MOVE
                shutil.move(old_path, new_path)
                
                print(Fore.GREEN + f"✔ Renamed: {filename} -> {metadata.category}/{new_filename}")
                print(Style.DIM + f"  Description: {metadata.description}")
            
            print("-" * 40)

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # TASK: Create a folder named 'my_gallery' and put some test images in it!
    folder_to_organize = "my_gallery"
    
    agent = SmartGalleryAgent(folder_to_organize)
    agent.organize()