import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_tone_agent(customer_query: str) -> dict:
    """
    Tone & Clarity Agent.
    Ensures the response is polite, clear and customer friendly.
    """

    # Step 1 - Build the prompt for Gemini
    prompt = f"""
    You are a Tone and Clarity Agent for a customer support system.

    Your job is to:
    1. Ensure the response to the customer is polite and empathetic
    2. Ensure the language is simple and easy to understand
    3. Ensure the response does not sound robotic or dismissive
    4. Provide a well worded customer friendly response fragment
    5. Assign a confidence score between 0 and 1

    Customer Query: {customer_query}

    Respond in this exact JSON format:
    {{
        "tone_issues": ["issue1 or empty list if none"],
        "clarity_issues": ["issue1 or empty list if none"],
        "response_fragment": "A polite and clear response fragment",
        "severity": "low",
        "confidence_score": 0.0
    }}

    Respond with JSON only. No extra text.
    """

    # Step 2 - Call Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Step 3 - Parse and return the result
    raw = response.text.strip().replace("```json", "").replace("```", "")
    result = json.loads(raw)
    result["agent"] = "tone"
    return result