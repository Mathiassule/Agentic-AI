import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from PIL import Image
from colorama import init, Fore

# Initialize
init(autoreset=True)
load_dotenv()

# ==========================================
# 1. DEFINE THE SCHEMA (Pydantic)
# ==========================================
# This acts as the "Contract" for the Vision model.
class ReceiptItem(BaseModel):
    item_name: str = Field(description="Name of the product purchased")
    price: float = Field(description="Price of the single item")

class Receiptdata(BaseModel):
    store_name: str = Field(description="Name of the merchant/store")
    date: str = Field(description="Date of purchase in YYYY-MM-DD format")
    total_amount: float = Field(description="The final total paid")
    items: list[ReceiptItem] = Field(description="List of line items on the receipt")
    currency: str = Field(description="Currency symbol or code (e.g., USD, NGN)")

# ==========================================
# 2. SETUP CLIENT (New SDK)
# ==========================================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_receipt_data(image_path):
    print(Fore.CYAN + f"📸 Loading receipt: {image_path}...")
    
    try:
        image = Image.open(image_path)
        
        prompt = "Analyze this receipt image and extract the data strictly matching the schema."

        print(Fore.YELLOW + "🤖 Extracting structured data from pixels...")

        # 3. GENERATE WITH SCHEMA ENFORCEMENT
        # The new SDK allows passing the Pydantic class directly into 'response_schema'
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=Receiptdata
            )
        )
        
        # 4. PARSE & DISPLAY
        # The response is already strictly formatted JSON text
        if response.text:
            data = json.loads(response.text)
            
            print(Fore.GREEN + "\n✔ EXTRACTION SUCCESS:")
            print(f"Store: {data['store_name']}")
            print(f"Date:  {data['date']}")
            print(f"Total: {data['total_amount']} {data['currency']}")
            print("\nItems:")
            for item in data['items']:
                print(f" - {item['item_name']}: {item['price']}")
            
            # Verify structure matches Pydantic (Optional double-check)
            validated = Receiptdata(**data)
            print(Fore.BLUE + f"\n[System] Validated as {type(validated).__name__} object.")

    except FileNotFoundError:
        print(Fore.RED + "Error: Receipt image not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # TASK: Download a receipt image and name it 'receipt.jpg'
    my_image = "receipt.png"
    
    if not os.path.exists(my_image):
        print(Fore.RED + f"⚠ Please place a receipt image named '{my_image}' in this folder.")
    else:
        extract_receipt_data(my_image)