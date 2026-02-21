import os
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE SHARED MEMORY (The Blackboard)
# ==========================================
# This dictionary is our "State". It gets passed to every agent.
shared_state = {
    "topic": "The discovery of Penicillin",
    "research_notes": "",
    "first_draft": "",
    "critic_feedback": ""
}

# ==========================================
# 2. THE AGENTS
# ==========================================
def researcher_agent(state):
    print(Fore.CYAN + f"\n[Researcher] 🔎 Researching: {state['topic']}...")
    prompt = f"Provide 3 raw, historical facts about: {state['topic']}."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    # Write to memory
    state["research_notes"] = response.text
    print(Fore.CYAN + "   -> Saved notes to shared memory.")
    return state

def writer_agent(state):
    print(Fore.YELLOW + f"\n[Writer] ✍️ Drafting based on research...")
    prompt = f"""
    Write a short, engaging 2-sentence summary based ON THESE NOTES ONLY:
    {state['research_notes']}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    # Write to memory
    state["first_draft"] = response.text
    print(Fore.YELLOW + "   -> Saved draft to shared memory.")
    return state

def critic_agent(state):
    print(Fore.MAGENTA + f"\n[Critic] 🧐 Reviewing the draft against original notes...")
    # The Critic reads BOTH the draft and the original notes from the state!
    prompt = f"""
    You are a strict editor. 
    Compare the ORIGINAL NOTES to the FIRST DRAFT. 
    Did the writer miss any crucial facts from the notes? Be brief.
    
    ORIGINAL NOTES: {state['research_notes']}
    FIRST DRAFT: {state['first_draft']}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    # Write to memory
    state["critic_feedback"] = response.text
    print(Fore.MAGENTA + "   -> Saved feedback to shared memory.")
    return state

# ==========================================
# 3. THE ORCHESTRATOR
# ==========================================
def run_system():
    global shared_state
    print(Fore.WHITE + Style.BRIGHT + "🚀 STARTING MULTI-AGENT SYSTEM\n")
    
    # Run the sequence, passing the state along
    shared_state = researcher_agent(shared_state)
    shared_state = writer_agent(shared_state)
    shared_state = critic_agent(shared_state)
    
    # Final Output
    print(Fore.GREEN + "\n✅ SYSTEM EXECUTION COMPLETE. FINAL STATE:")
    print(Style.DIM + "-" * 50)
    print(Fore.CYAN + f"RESEARCH:\n{shared_state['research_notes'].strip()}\n")
    print(Fore.YELLOW + f"DRAFT:\n{shared_state['first_draft'].strip()}\n")
    print(Fore.MAGENTA + f"FEEDBACK:\n{shared_state['critic_feedback'].strip()}\n")
    print(Style.DIM + "-" * 50)

if __name__ == "__main__":
    run_system()