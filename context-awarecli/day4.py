import os
import google.generativeai as genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# 1. Initialize Colorama (autoreset=True resets color after each print)
init(autoreset=True)

# 2. Load Env & Configure API
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 3. Persona
persona = """
You are a 'Futurist'. 
You answer every question by speculating how it will evolve in the year 2050.
Be vivid, optimistic, and descriptive.
"""

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite',
    system_instruction=persona
)

chat_session = model.start_chat(history=[])

print(Fore.CYAN + Style.BRIGHT + "🚀 2050 Vision Terminal Online. Ask about the future...")
print(Fore.CYAN + "-------------------------------------------------------------")

while True:
    try:
        user_input = input(Fore.YELLOW + "\nYou > " + Style.RESET_ALL)
        if user_input.lower() in ["exit", "quit"]:
            break
        
        print(Fore.GREEN + "Futurist > ", end="", flush=True)

        # 4. STREAMING IMPLEMENTATION
        # We set stream=True. 'response' is now a generator, not a string.
        response = chat_session.send_message(user_input, stream=True)
        
        # 5. Iterate through chunks as they arrive
        for chunk in response:
            # print with end="" to avoid newlines between chunks
            # flush=True ensures it prints immediately
            print(Fore.GREEN + chunk.text, end="", flush=True)
        
        print() # Print a final newline after the stream finishes

    except Exception as e:
        print(Fore.RED + f"\nError: {e}")

print(Fore.CYAN + "\nSystem Offline.")