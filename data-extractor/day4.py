import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, Field, field_validator
from colorama import init, Fore

init(autoreset=True)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. DEFINE STRICT RULES (The Validator)
# ==========================================
class EventSchema(BaseModel):
    event_name: str
    date: str = Field(description="Format YYYY-MM-DD")
    attendees: int

    # Custom Rule: The event MUST be in 2026.
    @field_validator('date')
    @classmethod
    def check_year(cls, v):
        if not v.startswith("2026"):
            raise ValueError(f"Date {v} is invalid. The event MUST be in the year 2026.")
        return v

# ==========================================
# 2. SETUP MODEL
# ==========================================
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite',
    generation_config={"response_mime_type": "application/json"}
)

# 3. THE INPUT (Tricky Data)
# Note: The text says "next Friday", which implies 2026 since we are in Feb 2026,
# but models often default to their training data cutoff or 'current year' if confused.
# We will see if it passes or fails, and if the loop fixes it.
user_text = """
Schedule the AI Summit for February 13th, 2025.
We are expecting about 50 people.
"""

# ==========================================
# 4. THE SELF-HEALING LOOP
# ==========================================
def extract_with_retry(text, max_retries=3):
    # Initial Prompt
    prompt = f"""
    Extract event details from the text below into JSON.
    Today's date is Feb 5, 2026.
    
    Schema: {EventSchema.model_json_schema()}
    
    Text: {text}
    """

    for attempt in range(max_retries):
        print(Fore.CYAN + f"\n[Attempt {attempt + 1}/{max_retries}] Asking Gemini...")
        
        try:
            # Generate
            response = model.generate_content(prompt)
            raw_json = json.loads(response.text)
            print(Fore.WHITE + f"AI Output: {raw_json}")

            # Validate (This is where it might fail)
            validated_data = EventSchema(**raw_json)
            
            print(Fore.GREEN + "✔ Success! Data is valid.")
            return validated_data

        except (ValidationError, json.JSONDecodeError) as e:
            # FAILURE CATCHER
            print(Fore.RED + f"❌ Validation Failed: {e}")
            print(Fore.YELLOW + "↺ Feeding error back to Gemini for correction...")
            
            # CRITICAL STEP: We update the prompt with the error info
            # This is "Reflexion" - letting the model think about its mistake.
            error_msg = str(e)
            prompt += f"\n\nSYSTEM ERROR: The previous JSON was invalid. \nReason: {error_msg}\nFIX THE JSON AND RETURN IT AGAIN."

    print(Fore.RED + "💀 Max retries reached. Extraction failed.")
    return None

# Run it
final_data = extract_with_retry(user_text)

if final_data:
    print(Fore.MAGENTA + f"\nFinal Result: {final_data.event_name} on {final_data.date}")