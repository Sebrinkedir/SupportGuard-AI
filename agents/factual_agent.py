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

    faq_topics = ["billing", "account_access", "technical", "policy_clarification"]
    faq_context = ""
    for topic in faq_topics:
        try:
            result = query_faq(topic)
            if result["status"] == "found":
                faq_context += json.dumps(result["results"]) + "\n"
        except Exception as e:
            logger.warning(f"FAQ tool failed for topic {topic}: {e}")

    prompt = f"""
    You are a Factual Grounding Agent for a customer support system.

    Your job is to:
    1. Check that claims made in response to the customer are supported by the FAQ documents
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
            "unsupported_claims": ["Could not verify claims due to a system error"],
            "response_fragment": "For accurate information, please refer to our Help Center or contact support.",
            "severity": "high",
            "confidence_score": 0.3,
            "error": "json_parse_error"
        }
    except Exception as e:
        logger.error(f"Factual agent unexpected error: {e}")
        return {
            "agent": "factual",
            "supported_claims": [],
            "unsupported_claims": ["Could not verify claims due to a system error"],
            "response_fragment": "For accurate information, please refer to our Help Center or contact support.",
            "severity": "high",
            "confidence_score": 0.3,
            "error": str(e)
        }