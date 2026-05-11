import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from tools.query_faq import query_faq

load_dotenv()
logger = logging.getLogger(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_intent_agent(customer_query: str) -> dict:
    """
    Intent Analysis Agent.
    Classifies the customer query and identifies what information is needed.
    """

    faq_topics = ["billing", "account_access", "technical", "policy_clarification"]
    faq_context = ""
    for topic in faq_topics:
        result = query_faq(topic)
        if result["status"] == "found":
            faq_context += json.dumps(result["results"]) + "\n"

    prompt = f"""
    You are an Intent Analysis Agent for a customer support system.

    Your job is to:
    1. Classify the customer query into one of these topics:
       billing, account_access, technical, policy_clarification
    2. Identify the key elements that a response must address
    3. Provide a helpful response fragment
    4. Assign severity:
       - high: billing and account issues
       - medium: technical issues
       - low: general questions only
    5. Assign confidence between 0.7 and 1.0 if you can provide a helpful response.
       Only go below 0.7 if the query is completely outside your knowledge.

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

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(raw)
        result["agent"] = "intent"
        logger.info(f"Intent agent completed | topic: {result.get('topic')} | confidence: {result.get('confidence_score')}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Intent agent JSON parse error: {e}")
        return {
            "agent": "intent",
            "topic": "unknown",
            "key_elements": [],
            "response_fragment": "Thank you for contacting support. We will look into your query.",
            "severity": "medium",
            "confidence_score": 0.7,
            "error": "json_parse_error"
        }
    except Exception as e:
        logger.error(f"Intent agent unexpected error: {e}")
        return {
            "agent": "intent",
            "topic": "unknown",
            "key_elements": [],
            "response_fragment": "Thank you for contacting support. We will look into your query.",
            "severity": "medium",
            "confidence_score": 0.7,
            "error": str(e)
        }