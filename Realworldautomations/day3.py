import os
import requests
import json
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE API TOOL
# ==========================================
def fetch_github_profile(username):
    """Hits the public GitHub API and returns structured JSON data."""
    print(Fore.CYAN + f"  [API Tool 🔌] Fetching data for GitHub user: @{username}...")
    
    url = f"https://api.github.com/users/{username}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            return f"Error: User '{username}' not found."
        
        response.raise_for_status() # Catch other HTTP errors
        
        # We got the data! Convert it to a Python dictionary
        data = response.json()
        
        # We don't need *every* field, so let's filter out the noise to save tokens
        filtered_data = {
            "name": data.get("name"),
            "company": data.get("company"),
            "location": data.get("location"),
            "bio": data.get("bio"),
            "public_repos": data.get("public_repos"),
            "followers": data.get("followers"),
            "created_at": data.get("created_at")
        }
        
        print(Fore.YELLOW + "  [API Tool 🔌] Data successfully retrieved!")
        # Convert back to a string so the LLM can read it
        return json.dumps(filtered_data, indent=2)

    except requests.exceptions.RequestException as e:
        return f"API Connection Error: {e}"

# ==========================================
# 2. THE RECRUITER AGENT
# ==========================================
def recruiter_agent(username):
    print(Fore.WHITE + Style.BRIGHT + f"\n🚀 STARTING PROFILE ANALYSIS FOR: @{username}")
    
    # 1. Get the live data from the API
    raw_api_data = fetch_github_profile(username)
    
    if "Error" in raw_api_data:
        print(Fore.RED + raw_api_data)
        return

    print(Fore.MAGENTA + "  [Agent 🧠] Synthesizing the API JSON data...")
    
    # 2. Pass the JSON to Gemini
    prompt = f"""
    You are a Technical Recruiter for a top-tier software company.
    Review the following JSON data pulled directly from the candidate's GitHub API.
    
    Write a brief, punchy 3-bullet-point summary of this candidate's profile, 
    and give a 1-sentence verdict on whether they seem active and experienced.
    
    GITHUB API DATA:
    {raw_api_data}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    
    print(Fore.GREEN + f"\n✅ RECRUITER REPORT:\n")
    print(Fore.WHITE + response.text)
    print(Style.DIM + "-" * 50)

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # TASK: Change this to your own GitHub username (or anyone else's, like 'torvalds' for Linus Torvalds!)
    target_user = "Mathiassule" 
    
    recruiter_agent(target_user)