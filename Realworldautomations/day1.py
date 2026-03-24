import os
import requests
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE BROWSER TOOL (Web Scraper)
# ==========================================
def scrape_website(url):
    """Fetches a URL and extracts the readable text."""
    print(Fore.CYAN + f"  [Scraper 🌐] Fetching live data from: {url}")
    
    try:
        # Pretend to be a normal browser so websites don't block us
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Check for HTTP errors (like 404)
        
        # Parse HTML and extract text
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        
        # Truncate text if it's massively long (to save tokens, though Gemini handles a lot)
        return text[:15000] 
        
    except Exception as e:
        return f"Error scraping website: {e}"

# ==========================================
# 2. THE ANALYST AGENT
# ==========================================
def web_analyst_agent(url, query):
    """Scrapes the URL and answers the user's specific query based on the content."""
    
    # 1. Use the tool to get the raw data
    raw_web_text = scrape_website(url)
    
    if raw_web_text.startswith("Error"):
        print(Fore.RED + raw_web_text)
        return
        
    print(Fore.YELLOW + "  [Agent 🧠] Reading the webpage content...")
    
    # 2. Build the prompt with the live context
    prompt = f"""
    You are a Technical Research Assistant. 
    Read the following webpage content and answer the user's query. 
    If the answer is not in the text, say "I cannot find this in the provided article."
    
    USER QUERY: {query}
    
    WEBPAGE CONTENT:
    {raw_web_text}
    """
    
    # 3. Generate response
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    
    print(Fore.GREEN + f"\n✅ INSIGHTS:\n{response.text}")
    print(Style.DIM + "-" * 50)

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    print(Fore.WHITE + Style.BRIGHT + "🚀 STARTING WEB ANALYST AGENT\n")
    
    # We are scraping a Wikipedia page on Computer Vision
    target_url = "https://en.wikipedia.org/wiki/Computer_vision"
    user_query = "What are the typical tasks or sub-domains involved in this field? Give me a bulleted list."
    
    web_analyst_agent(target_url, user_query)