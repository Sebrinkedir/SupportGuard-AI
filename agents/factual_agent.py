import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from tools.query_faq import query_faq

load_dotenv()
logger = logging.getLogger(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_factual_agent(customer_query: str) -> dict:
    """
    Factual Grounding Agent.
    Ensures all claims are supported by FAQ documents.
    """

    faq_topics = ["billing", "account_access", "technical", "policy_clarification"]
    faq_context = ""
    for topic in faq_topics:
        result = query_faq(topic)
        if result["status"] == "found":
            faq_context += json.dumps(result["results"]) + "\n"

    prompt = f"""
    You are a Factual Grounding Agent for a customer support system.

    Your job is to:
    1. Check that claims made in response to the customer are supported by the FAQ documents
    2. Flag any information that cannot be verified from the documents
    3. Provide a factually grounded response fragment
    4. Assign severity:
       - high: claims are fully supported by documents
       - medium: claims are partially supported
       - low: claims are unsupported
    5. Assign confidence between 0.7 and 1.0 if you can provide a helpful response.
       Only go below 0.7 if the query is completely outside your knowledge.

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

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(raw)
        result["agent"] = "factual"
        logger.info(f"Factual agent completed | supported: {len(result.get('supported_claims', []))} | unsupported: {len(result.get('unsupported_claims', []))}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Factual agent JSON parse error: {e}")
        return {
            "agent": "factual",
            "supported_claims": [],
            "unsupported_claims": [],
            "response_fragment": "Based on our records, we will investigate your query and respond shortly.",
            "severity": "medium",
            "confidence_score": 0.7,
            "error": "json_parse_error"
        }
    except Exception as e:
        logger.error(f"Factual agent unexpected error: {e}")
        return {
            "agent": "factual",
            "supported_claims": [],
            "unsupported_claims": [],
            "response_fragment": "Based on our records, we will investigate your query and respond shortly.",
            "severity": "medium",
            "confidence_score": 0.7,
            "error": str(e)
        }