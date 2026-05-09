import os
import json
from dotenv import load_dotenv
from google import genai
from tools.query_faq import query_faq

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_factual_agent(customer_query: str) -> dict:
    """
    Factual Grounding Agent.
    Ensures all claims in the response are supported by FAQ documents.
    """

    # Step 1 - Use MCP tool to fetch all FAQ context
    faq_topics = ["billing", "account_access", "technical", "policy_clarification"]
    faq_context = ""
    for topic in faq_topics:
        result = query_faq(topic)
        if result["status"] == "found":
            faq_context += json.dumps(result["results"]) + "\n"

    # Step 2 - Build the prompt for Gemini
    prompt = f"""
    You are a Factual Grounding Agent for a customer support system.

    Your job is to:
    1. Check that any claims made in response to the customer are 
       supported by the FAQ documents provided
    2. Flag any information that cannot be verified from the documents
    3. Provide a factually grounded response fragment
    4. Assign a confidence score between 0 and 1

    Customer Query: {customer_query}

    FAQ Documents:
    {faq_context}

    Respond in this exact JSON format:
    {{
        "supported_claims": ["claim1", "claim2"],
        "unsupported_claims": ["claim1 or empty list if none"],
        "response_fragment": "A factually grounded response fragment",
        "severity": "high or medium or low",
        "confidence_score": 0.0
    }}

    Respond with JSON only. No extra text.
    """

    # Step 3 - Call Gemini
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = response.text.strip().replace("```json", "").replace("```", "")

    # Step 4 - Parse and return the result
    raw = response.text.strip().replace("```json", "").replace("```", "")
    result = json.loads(raw)
    result["agent"] = "factual"
    return result