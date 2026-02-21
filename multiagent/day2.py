import os
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()

# Setup Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. DEFINE AGENT A: THE RESEARCHER
# ==========================================
def researcher_agent(topic):
    print(Fore.CYAN + f"\n[Researcher] 🔎 Gathering raw facts on: '{topic}'...")
    
    prompt = f"""
    You are a Senior Research Analyst.
    Find 3 distinct, interesting, and technical facts about: {topic}.
    Return ONLY the facts as a bulleted list. No intro, no outro.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    return response.text

# ==========================================
# 2. DEFINE AGENT B: THE WRITER
# ==========================================
def writer_agent(raw_data):
    print(Fore.YELLOW + f"\n[Writer] ✍️  Drafting content based on research...")
    
    prompt = f"""
    You are a viral social media ghostwriter.
    Take the following raw research data and turn it into a punchy, engaging LinkedIn post.
    Use emojis, short sentences, and a strong hook.
    
    RAW DATA:
    {raw_data}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    return response.text

# ==========================================
# 3. THE ORCHESTRATOR (The Chain)
# ==========================================
def run_content_chain(topic):
    print(Fore.WHITE + f"🚀 STARTING CHAIN FOR TOPIC: {topic}")
    print(Style.DIM + "------------------------------------------------")
    
    # STEP 1: Research
    # We capture the output into a variable
    research_output = researcher_agent(topic)
    
    print(Fore.CYAN + f"\n   (Internal Data Passing): \n   {research_output.strip()[:100]}...") 

    # STEP 2: Write
    # We pass the variable from Step 1 into Step 2
    final_post = writer_agent(research_output)
    
    # RESULT
    print(Fore.GREEN + "\n✅ FINAL OUTPUT:\n")
    print(final_post)
    print(Style.DIM + "------------------------------------------------")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # Try changing this to anything!
    topic = "The Future of AI Agents"
    
    run_content_chain(topic)