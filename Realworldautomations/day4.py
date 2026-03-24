import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from colorama import init, Fore

# Initialize
init(autoreset=True)
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. SETUP THE SERVER
# ==========================================
# This creates our web application
app = FastAPI(
    title="Agentic OS Webhook",
    description="A local REST API for my AI Agent."
)

# Define the exact JSON structure the server expects to receive
class AgentRequest(BaseModel):
    prompt: str
    context: str = "general" # Optional field with a default

# ==========================================
# 2. THE AGENT LOGIC
# ==========================================
def process_query(prompt: str, context: str):
    """The brain of the operation."""
    print(Fore.CYAN + f"\n[Agent 🧠] Processing query: '{prompt}' (Context: {context})")
    
    system_instruction = f"You are a helpful API agent. The user context is: {context}."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[system_instruction, prompt]
        )
        print(Fore.GREEN + "  -> Response generated successfully.")
        return response.text
    except Exception as e:
        print(Fore.RED + f"  -> Error: {e}")
        raise HTTPException(status_code=500, detail="Agent processing failed")

# ==========================================
# 3. THE WEBHOOK ENDPOINT
# ==========================================
@app.post("/webhook/agent")
async def trigger_agent(request: AgentRequest):
    """
    This is the 'door' to our agent. 
    It listens for POST requests at http://localhost:8000/webhook/agent
    """
    print(Fore.YELLOW + f"📥 [Server] Received POST request at /webhook/agent")
    
    # Pass the incoming data to the AI
    answer = process_query(request.prompt, request.context)
    
    # Return a structured JSON response to the sender
    return {
        "status": "success",
        "original_prompt": request.prompt,
        "agent_response": answer
    }

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    print(Fore.MAGENTA + "🚀 Starting Agent Server on http://localhost:8000")
    print(Fore.MAGENTA + "   You can view the auto-generated docs at http://localhost:8000/docs")
    print(Fore.MAGENTA + "   Press CTRL+C to stop the server.")
    
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)