import os
import json
import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, Field, EmailStr
from typing import List, Optional
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE DATA SCHEMA (The "Contract")
# ==========================================
class CRMRecord(BaseModel):
    client_name: str = Field(description="Name of the company or client")
    contact_email: Optional[str] = Field(description="Email address if available, else null")
    deal_value: int = Field(description="Estimated deal value in USD (integers only, no currency symbols)")
    sentiment: str = Field(description="One of: 'Hot', 'Warm', 'Cold'")
    next_action_date: str = Field(description="YYYY-MM-DD format. Calculate based on 'next Friday' logic if needed.")
    action_items: List[str] = Field(description="List of specific tasks to do")

# ==========================================
# 2. THE AGENT CLASS
# ==========================================
class AutoCRMAgent:
    def __init__(self, model_name='gemini-2.5-flash-lite'):
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )
        print(Fore.GREEN + f"✔ Auto-CRM Agent initialized with {model_name}")

    def process_notes(self, raw_notes: str, max_retries=3):
        """
        Takes raw text, extracts structured data, validates it, and auto-heals if needed.
        """
        # Context for the AI (Current date helps with "next Friday" logic)
        today = datetime.date.today()
        
        prompt = f"""
        You are a Data Entry Clerk. 
        Extract client details from the NOTES below into a JSON object.
        
        CURRENT DATE: {today}
        
        RULES:
        1. Convert '10k' to 10000.
        2. Calculate specific dates (e.g., 'next week' -> YYYY-MM-DD).
        3. If email is missing, use null.
        
        TARGET SCHEMA:
        {CRMRecord.model_json_schema()}
        
        NOTES:
        {raw_notes}
        """

        print(Fore.CYAN + "\n[System] Processing notes...")

        for attempt in range(max_retries):
            try:
                # 1. Generate
                response = self.model.generate_content(prompt)
                raw_json = json.loads(response.text)
                
                # 2. Validate (Pydantic Magic)
                # This line throws an error if data is bad
                validated_record = CRMRecord(**raw_json)
                
                # 3. Success
                print(Fore.GREEN + f"✔ Extraction Successful (Attempt {attempt+1})")
                return validated_record

            except (ValidationError, json.JSONDecodeError) as e:
                print(Fore.YELLOW + f"⚠ Attempt {attempt+1} Failed: {e}")
                print(Fore.YELLOW + "↺ Self-correcting...")
                
                # 4. Reflexion (Feedback Loop)
                # Append the error to the prompt so the AI knows what to fix
                prompt += f"\n\nPREVIOUS ERROR: {str(e)}\nFIX THE JSON AND RETURN IT."
        
        print(Fore.RED + "❌ Failed to extract valid data after retries.")
        return None

    def save_to_db(self, record: CRMRecord):
        """Simulates saving to a database"""
        if not record:
            return
            
        print(Fore.MAGENTA + "\n💾 SAVING TO DATABASE...")
        print(Style.BRIGHT + "------------------------------------------------")
        print(f"CLIENT:   {record.client_name}")
        print(f"VALUE:    ${record.deal_value:,}")
        print(f"STATUS:   {record.sentiment}")
        print(f"DUE DATE: {record.next_action_date}")
        print(f"TASKS:    {record.action_items}")
        print(Style.BRIGHT + "------------------------------------------------")
        print(Fore.GREEN + "✔ Record Saved ID: #88219")

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    agent = AutoCRMAgent()

    # The messy input
    messy_notes = """
    Just got off the phone with 'TechNova Solutions'. 
    Ideally they want to start the project by March 1st.
    Budget is tight, around 15k, but they are super keen, so mark it as Hot.
    We need to email the slide deck to sarah.j@technova.io.
    Also, set a reminder to call them back next Monday for the contract signing.
    """
    
    # Run the Pipeline
    print(Fore.WHITE + "INPUT NOTES:\n" + messy_notes)
    
    clean_record = agent.process_notes(messy_notes)
    agent.save_to_db(clean_record)