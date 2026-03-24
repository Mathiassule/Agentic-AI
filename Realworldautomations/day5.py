import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE SCRAPING TOOL
# ==========================================
def scrape_article(url):
    """Fetches a URL and extracts the clean text."""
    print(Fore.CYAN + f"  [Scraper 🌐] Reading: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return text[:10000] # Limit tokens per article
    except Exception as e:
        print(Fore.RED + f"  [Error] Failed to scrape {url}: {e}")
        return ""

# ==========================================
# 2. THE SYNTHESIS AGENT
# ==========================================
def generate_briefing(articles_data):
    """Takes all scraped raw text and writes a master summary."""
    print(Fore.MAGENTA + "\n  [Agent 🧠] Synthesizing all data into a Morning Briefing...")
    
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    
    prompt = f"""
    You are an elite Executive Assistant.
    Today is {today_str}.
    
    Read the following raw data scraped from multiple tech websites this morning.
    Write a cohesive, engaging "Morning Briefing" report.
    
    Format the output in clean Markdown. Include:
    1. A catchy main title.
    2. A 2-sentence executive summary at the top.
    3. 3-4 bullet points highlighting the most important news.
    4. A brief "Takeaway" section on why this matters for the tech industry.
    
    RAW DATA:
    {articles_data}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    return response.text

# ==========================================
# 3. FILE MANAGEMENT
# ==========================================
def save_report(content):
    """Saves the markdown content to a file."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"Briefing_{date_str}.md"
    
    # Create a 'reports' folder if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    filepath = os.path.join("reports", filename)
    
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)
        
    print(Fore.GREEN + f"\n✅ Report successfully saved to: {filepath}")

# ==========================================
# EXECUTION (The Workflow)
# ==========================================
def run_morning_routine():
    print(Fore.WHITE + Style.BRIGHT + "🌅 INITIATING MORNING ROUTINE...\n")
    
    # 1. Define the targets (These can be any public article URLs)
    target_urls = [
        "https://en.wikipedia.org/wiki/Large_language_model",
        "https://en.wikipedia.org/wiki/Artificial_general_intelligence",
        "https://en.wikipedia.org/wiki/Agent_architecture"
    ]
    
    # 2. Scrape all targets
    compiled_raw_data = ""
    for url in target_urls:
        article_text = scrape_article(url)
        if article_text:
            compiled_raw_data += f"\n\n--- Source: {url} ---\n{article_text}"
            
    if not compiled_raw_data.strip():
        print(Fore.RED + "❌ All scraping failed. Aborting routine.")
        return

    # 3. Generate the report
    final_report = generate_briefing(compiled_raw_data)
    
    # 4. Save to disk
    save_report(final_report)
    
    print(Style.DIM + "-" * 50)
    print(Fore.YELLOW + "Preview of your briefing:")
    print(final_report[:300] + "...\n(Read the full .md file for the rest!)")

if __name__ == "__main__":
    run_morning_routine()