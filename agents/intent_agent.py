import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from tools.query_faq import query_faq

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_intent_agent(customer_query: str) -> dict:
    """
    Intent Analysis Agent.
    Classifies the customer query and identifies what information is needed.
    """

    # Step 1 - Use MCP tool to fetch all FAQ topics
    faq_topics = ["billing", "account_access", "technical", "policy_clarification"]
    faq_context = ""
    for topic in faq_topics:
        result = query_faq(topic)
        if result["status"] == "found":
            faq_context += json.dumps(result["results"]) + "\n"

    # Step 2 - Build the prompt for Gemini
    prompt = f"""
    You are an Intent Analysis Agent for a customer support system.
    
    Your job is to:
    1. Classify the customer query into one of these topics:
       billing, account_access, technical, policy_clarification
    2. Identify the key elements that a response must address
    3. Assign a confidence score between 0 and 1

    Customer Query: {customer_query}

    Available FAQ Context:
    {faq_context}

    Respond in this exact JSON format:
    {{
        "topic": "billing or account_access or technical or policy_clarification",
        "key_elements": ["element1", "element2"],
        "response_fragment": "A brief response addressing the intent",
        "severity": "high or medium or low",
        "confidence_score": 0.0
    }}

    Respond with JSON only. No extra text.
    """

    # Step 3 - Call Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Step 4 - Parse and return the result
    raw = response.text.strip().replace("```json", "").replace("```", "")
    result = json.loads(raw)
    result["agent"] = "intent"
    return result