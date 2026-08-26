import json
import os
import re
import traceback
import google.generativeai as genai

# Configure your API Key (In production, move this to a .env file!)
gcp_api_key = os.getenv("GCP_API_KEY")

# We use Gemini 1.5 Flash for speed, forcing it to return strict JSON
model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    generation_config={"response_mime_type": "application/json"}
)

async def analyze_payment_failure(customer_name: str, amount: int, failure_reason: str, method: str) -> dict:
    """
    Sends the exact payment failure context to Gemini to predict the best recovery strategy.
    """
    formatted_amount = amount / 100
    
    prompt = f"""
    You are an expert AI debt recovery agent for an Indian merchant. 
    Analyze this failed transaction and predict the best recovery strategy.
    
    Customer Name: {customer_name}
    Amount: ₹{formatted_amount}
    Payment Method: {method}
    Failure Reason: {failure_reason}
    
    Return ONLY a JSON object with these exact keys:
    - "recovery_probability": an integer between 0 and 100 representing the likelihood they will pay if reminded.
    - "optimal_channel": the best channel to reach them (choose from: "whatsapp", "sms", or "email").
    - "delay_hours": how many hours we should wait before sending the reminder (integer). If it's a simple timeout, delay should be 1. If it's insufficient funds, delay should be 24 or 48.
    - "personalized_message": A short, polite, empathetic 1-2 sentence message urging them to complete the payment via a new link.
    """
    
    try:
        # Use the async generation method for FastAPI
        response = await model.generate_content_async(prompt)
        raw_text = response.text.strip()
        
        # Clean up Markdown formatting just in case
        if raw_text.startswith("```json"):
            raw_text = re.sub(r"^```json\n|\n```$", "", raw_text)
        elif raw_text.startswith("```"):
            raw_text = re.sub(r"^```\n|\n```$", "", raw_text)
            
        # Parse the AI's JSON output into a Python dictionary
        ai_decision = json.loads(raw_text)
        return ai_decision
        
    except Exception as e:
        # Print the full traceback to the terminal so we can see the exact error
        print("\n--- AI AGENT ERROR ---")
        traceback.print_exc()
        print("----------------------\n")
        
        # Fallback in case of an API timeout or error
        return {
            "recovery_probability": 50,
            "optimal_channel": "email",
            "delay_hours": 2,
            "personalized_message": f"Hi {customer_name}, your payment of ₹{formatted_amount} failed. Please try again."
        }