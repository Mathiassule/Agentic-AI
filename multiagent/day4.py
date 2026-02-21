import os
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE "DANGEROUS" TOOL (Requires HITL)
# ==========================================
def execute_refund(amount, customer):
    """A high-risk action that interacts with 'real' money."""
    print(Fore.RED + Style.BRIGHT + f"\n💰 [SYSTEM ALERT] DANGEROUS ACTION INITIATED")
    print(Fore.RED + f"The Agent wants to process a ${amount} refund to {customer}.")
    
    # --- THE HUMAN IN THE LOOP PAUSE ---
    print(Fore.YELLOW + "⚠️ HUMAN APPROVAL REQUIRED.")
    user_input = input(f"Approve this transaction? (Y/N): ").strip().upper()
    
    if user_input == 'Y':
        print(Fore.GREEN + f"✅ [SYSTEM] Refund of ${amount} Approved and Processed.")
        return "Success: Refund processed."
    else:
        print(Fore.RED + "❌ [SYSTEM] Refund Denied by Human Admin.")
        return "Failed: Admin rejected the refund request."

# ==========================================
# 2. THE AUTONOMOUS AGENT
# ==========================================
def customer_service_agent(complaint):
    print(Fore.CYAN + f"\n[Agent] 🤖 Analyzing customer message: '{complaint}'")
    
    prompt = f"""
    You are a customer service AI. Read the complaint.
    If the customer is extremely angry and explicitly asking for their money back, output EXACTLY: 'REFUND_NEEDED'.
    Otherwise, output EXACTLY: 'RESOLVE_NORMALLY'.
    
    Complaint: {complaint}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt
    )
    
    intent = response.text.strip()
    print(Fore.CYAN + f"   -> Agent Decision: {intent}")
    
    # 3. ROUTING LOGIC
    if "REFUND_NEEDED" in intent:
        print(Fore.YELLOW + "   -> Agent is requesting a financial tool...")
        # The agent tries to use the tool, hitting the HITL block.
        result = execute_refund(amount=50, customer="John Doe")
        return result
    else:
        print(Fore.GREEN + "   -> Agent resolved the issue autonomously with an email.")
        return "Success: Sent apology email."

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    print(Fore.WHITE + Style.BRIGHT + "--- TEST CASE 1: Low-Risk Task ---")
    customer_service_agent("My package arrived a day late, but it's fine. Just letting you know.")
    
    print(Fore.WHITE + Style.BRIGHT + "\n--- TEST CASE 2: High-Risk Task (Triggers HITL) ---")
    customer_service_agent("This product is completely broken! I demand my money back right now!")