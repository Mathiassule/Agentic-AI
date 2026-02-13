import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.ai.generativelanguage import Content, Part
from google.protobuf import struct_pb2
from colorama import init, Fore

init(autoreset=True)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. DEFINE YOUR TOOLS (Python Functions)
# ==========================================
# The docstring is CRITICAL. It tells the AI *how* and *when* to use this.
def check_flight_price(destination: str, date: str):
    """
    Retrieves the current flight price to a specific destination on a given date.
    
    Args:
        destination: The city or airport code (e.g., "Lagos", "LHR").
        date: The date of travel (e.g., "2026-03-01").
    """
    # In a real app, this would hit an API. Here we mock it.
    print(Fore.YELLOW + f"\n[SYSTEM] ✈️ Checking database for flights to {destination} on {date}...")
    
    if "Lagos" in destination:
        return {"price": 120000, "currency": "NGN", "airline": "Air Peace"}
    elif "London" in destination:
        return {"price": 850, "currency": "USD", "airline": "British Airways"}
    else:
        return {"price": 0, "error": "Destination not found"}

# ==========================================
# 2. BIND TOOLS TO MODEL
# ==========================================
# We create a dictionary of tools to pass to the model
tools_map = {'check_flight_price': check_flight_price}

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite', # Using your preferred version
    tools=[check_flight_price] # <--- WE GIVE THE MODEL THE TOOL HERE
)

# 3. START CHAT (Enable automatic function calling is the easiest way)
chat = model.start_chat(enable_automatic_function_calling=True)

# ==========================================
# 4. THE INTERACTION
# ==========================================
user_query = "I need to fly to Lagos on March 5th 2026. How much is it?"

print(Fore.CYAN + f"User: {user_query}")

response = chat.send_message(user_query)

# The library handles the back-and-forth automatically:
# 1. Model sees query -> Calls 'check_flight_price'
# 2. Code runs the function -> Returns {price: 120000...}
# 3. Model reads result -> Generates final answer
print(Fore.GREEN + f"Agent: {response.text}")

# Let's try a query that DOESN'T need a tool to prove it decides dynamically
user_query_2 = "Write a short poem about flying."
print(Fore.CYAN + f"\nUser: {user_query_2}")
response_2 = chat.send_message(user_query_2)
print(Fore.GREEN + f"Agent: {response_2.text}")