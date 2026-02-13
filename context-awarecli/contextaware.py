import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class GeminiAgent:
    def __init__(self, model_name='gemini-2.5-flash-lite', system_instruction=None):
        """Initializes the Agent with API configuration and Persona."""
        self._configure_api()
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_instruction
        )
        self.chat_session = None

    def _configure_api(self):
        """Loads API key and handles missing keys gracefully."""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(Fore.RED + "Error: GEMINI_API_KEY not found in .env file.")
            sys.exit(1)
        genai.configure(api_key=api_key)

    def start_chat(self):
        """Starts a new chat session with empty history."""
        self.chat_session = self.model.start_chat(history=[])
        print(Fore.GREEN + f"✔ Agent initialized ({self.model_name})")
        print(Fore.CYAN + "--------------------------------------------------")

    def chat_loop(self):
        """Main interaction loop."""
        if not self.chat_session:
            self.start_chat()

        print(Fore.YELLOW + "System: Ready. Type 'exit', 'quit', or 'clear' to reset.")

        while True:
            try:
                # 1. Get User Input
                user_input = input(Fore.BLUE + "\nYou > " + Style.RESET_ALL).strip()

                # 2. Handle Commands
                if user_input.lower() in ['exit', 'quit']:
                    print(Fore.YELLOW + "Ending session. Goodbye!")
                    break
                
                if user_input.lower() == 'clear':
                    self.start_chat() # Reset memory
                    print(Fore.YELLOW + "Memory cleared.")
                    continue

                if not user_input:
                    continue

                # 3. Generate & Stream Response
                print(Fore.MAGENTA + "Agent > " + Style.RESET_ALL, end="", flush=True)
                
                response_stream = self.chat_session.send_message(user_input, stream=True)
                
                for chunk in response_stream:
                    print(Fore.WHITE + chunk.text, end="", flush=True)
                
                print() # Newline after stream

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print(Fore.RED + "\n\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(Fore.RED + f"\nError: {e}")

# ==========================================
# USAGE
# ==========================================
if __name__ == "__main__":
    # Define your persona here easily
    MY_PERSONA = """
    You are an expert Python Tutor.
    You explain concepts simply and always provide a short code example.
    """

    agent = GeminiAgent(
        model_name='gemini-2.5-flash-lite', 
        system_instruction=MY_PERSONA
    )
    
    agent.chat_loop()