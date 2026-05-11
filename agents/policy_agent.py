import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from tools.lookup_refund_policy import lookup_refund_policy
from tools.check_account_permissions import check_account_permissions

load_dotenv()
logger = logging.getLogger(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_policy_agent(customer_query: str) -> dict:
    """
    Policy Compliance Agent.
    Ensures the response follows company policies and rules.
    """

    plans = ["free", "basic", "premium", "enterprise"]
    policy_context = ""
    for plan in plans:
        result = lookup_refund_policy(plan)
        if result["status"] == "found":
            policy_context += json.dumps(result["results"]) + "\n"

    actions = ["refund_processing", "issue_refund_promise", "account_deletion",
               "password_reset", "plan_upgrade", "plan_downgrade"]
    permissions_context = ""
    for action in actions:
        result = check_account_permissions(action)
        if result["status"] == "found":
            permissions_context += json.dumps(result["results"]) + "\n"

    prompt = f"""
    You are a Policy Compliance Agent for a customer support system.

    Your job is to:
    1. Check if the customer query involves any policy sensitive actions
    2. Ensure the response does NOT promise refunds directly
    3. Ensure the response follows correct refund rules per plan
    4. Assign severity:
       - high: any refund or policy sensitive query
       - medium: account changes
       - low: general questions only
    5. Assign confidence between 0.7 and 1.0 if you can provide a helpful response.
       Only go below 0.7 if the query is completely outside your knowledge.

    Customer Query: {customer_query}

    Refund Policies:
    {policy_context}

    Account Permissions:
    {permissions_context}

    Respond in this exact JSON format:
    {{
        "policy_compliant": true or false,
        "violations": ["violation1 or empty list if none"],
        "response_fragment": "A policy compliant response fragment",
        "severity": "high or medium or low",
        "confidence_score": 0.0
    }}

    Respond with JSON only. No extra text.
    """

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(raw)
        result["agent"] = "policy"
        logger.info(f"Policy agent completed | compliant: {result.get('policy_compliant')} | confidence: {result.get('confidence_score')}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Policy agent JSON parse error: {e}")
        return {
            "agent": "policy",
            "policy_compliant": True,
            "violations": [],
            "response_fragment": "Please contact our support team for assistance with this request.",
            "severity": "high",
            "confidence_score": 0.7,
            "error": "json_parse_error"
        }
    except Exception as e:
        logger.error(f"Policy agent unexpected error: {e}")
        return {
            "agent": "policy",
            "policy_compliant": False,
            "violations": [],
            "response_fragment": "Please contact our support team for assistance with this request.",
            "severity": "high",
            "confidence_score": 0.7,
            "error": str(e)
        }