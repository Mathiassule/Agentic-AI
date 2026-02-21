import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()

# ==========================================
# 1. DEFINE THE TOOLS (The Workers)
# ==========================================
def tool_math(query):
    print(Fore.YELLOW + f"  [Worker: MATH] Solving: {query}")
    # In a real app, you'd call a calculator or Python REPL here.
    return "Math Agent: I calculated the answer is 42."

def tool_search(query):
    print(Fore.CYAN + f"  [Worker: SEARCH] Googling: {query}")
    return "Search Agent: The weather in Lagos is 32°C."

def tool_chat(query):
    print(Fore.MAGENTA + f"  [Worker: CHAT] Thinking...")
    return "Chat Agent: That's an interesting philosophical question!"

# ==========================================
# 2. THE ROUTER (The Manager)
# ==========================================
class AgentRouter:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # The prompt that forces the model to choose a tool
        self.system_instruction = """
        You are a Router. You do not answer questions.
        You only classify the user's intent into one of these labels:
        
        - TOOL_MATH: For calculations, numbers, or logic puzzles.
        - TOOL_SEARCH: For current events, facts, weather, or news.
        - TOOL_CHAT: For casual conversation, greetings, or philosophy.
        
        Output ONLY the label. Do not explain.
        """

    def route_request(self, user_query):
        print(Fore.WHITE + f"\nUSER: {user_query}")
        print(Style.DIM + "  [Router] Deciding...")
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[self.system_instruction, f"Query: {user_query}"],
            config=types.GenerateContentConfig(
                temperature=0.0 # Strictness is key for routing
            )
        )
        
        intent = response.text.strip()
        print(Fore.GREEN + f"  [Router] Selected: {intent}")
        
        # 3. DISPATCH (The Switch)
        if intent == "TOOL_MATH":
            return tool_math(user_query)
        elif intent == "TOOL_SEARCH":
            return tool_search(user_query)
        elif intent == "TOOL_CHAT":
            return tool_chat(user_query)
        else:
            return f"Error: Unknown intent '{intent}'"

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    router = AgentRouter()
    
    # Test Cases
    queries = [
        "What is the square root of 144?",
        "Hello, how are you today?",
        "Who won the Super Bowl in 2025?",
        "Multiply 50 by 20"
    ]
    
    for q in queries:
        result = router.route_request(q)
        print(result)
        print("-" * 30)