import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE TOOLBOX
# ==========================================
def tool_calculator(expression):
    """Evaluates a math expression."""
    print(Fore.YELLOW + f"  [System ⚙️] Running calculator on: {expression}")
    try:
        # In production, NEVER use eval() for untrusted input. 
        # We use it here purely for a lightweight mock demonstration.
        result = eval(expression) 
        return f"The calculated result is: {result}"
    except Exception as e:
        return f"Math Error: {e}"

def tool_database_lookup(query):
    """Mocks searching an internal database."""
    print(Fore.CYAN + f"  [System 🔎] Searching secure database for: {query}")
    db = {"project alpha": "Due March 15th. Status: On track.", 
          "client omega": "Awaiting contract signature."}
    
    for key, value in db.items():
        if key in query.lower():
            return value
    return "No records found in the database."

# ==========================================
# 2. THE REASONING ENGINE (The Agent)
# ==========================================
def agent_reasoning_loop(user_input):
    """Determines the tool to use, executes it, and returns the final answer."""
    
    # STEP 1: PLAN
    system_instruction = """
    You are a Generalist CLI Agent. 
    Analyze the user's request and decide what to do.
    
    If the user asks a math question, output exactly this JSON:
    {"action": "CALCULATE", "param": "the_math_expression"}
    
    If the user asks about a project or client, output exactly this JSON:
    {"action": "DATABASE", "param": "project_name"}
    
    If it's a general conversation, output exactly this JSON:
    {"action": "CHAT", "param": "your_response"}
    """
    
    print(Style.DIM + "  [Agent] Thinking...")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=[system_instruction, f"User Request: {user_input}"],
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
    )
    
    try:
        plan = json.loads(response.text)
    except json.JSONDecodeError:
        return "System Error: Agent produced invalid plan."

    # STEP 2 & 3: ACT & OBSERVE
    action = plan.get("action")
    param = plan.get("param")
    
    if action == "CALCULATE":
        observation = tool_calculator(param)
    elif action == "DATABASE":
        observation = tool_database_lookup(param)
    else:
        # It's just a chat, the param *is* the response
        return param 

    # STEP 4: FINAL OUTPUT (Synthesize the observation)
    print(Style.DIM + "  [Agent] Synthesizing final response...")
    final_prompt = f"The user asked: '{user_input}'. The system returned this raw data: '{observation}'. Turn this into a natural, helpful response."
    
    final_response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=final_prompt
    )
    
    return final_response.text

# ==========================================
# 3. THE CLI REPL (Read-Eval-Print Loop)
# ==========================================
def start_cli():
    print(Fore.MAGENTA + Style.BRIGHT + "========================================")
    print(Fore.MAGENTA + Style.BRIGHT + "🧠 AGENTIC OS TERMINAL V1.0 INITIALIZED")
    print(Fore.MAGENTA + "Type 'exit' to shut down the system.")
    print(Fore.MAGENTA + Style.BRIGHT + "========================================\n")
    
    while True:
        try:
            # 1. READ
            user_input = input(Fore.WHITE + Style.BRIGHT + "\nUSER> ")
            
            if user_input.lower() in ['exit', 'quit']:
                print(Fore.RED + "\n[System] Shutting down. Goodbye! 👋")
                break
            
            if not user_input.strip():
                continue
                
            # 2. EVALUATE
            answer = agent_reasoning_loop(user_input)
            
            # 3. PRINT
            print(Fore.GREEN + f"\nAGENT> {answer.strip()}")
            
        except KeyboardInterrupt:
            print(Fore.RED + "\n[System] Forced shutdown detected. Goodbye!")
            break

if __name__ == "__main__":
    start_cli()