import os
import json
from dotenv import load_dotenv
from google import genai
from tools.lookup_refund_policy import lookup_refund_policy
from tools.check_account_permissions import check_account_permissions

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def run_policy_agent(customer_query: str) -> dict:
    """
    Policy Compliance Agent.
    Ensures the response follows company policies and rules.
    """

    # Step 1 - Use MCP tools to fetch policy context
    plans = ["free", "basic", "premium", "enterprise"]
    policy_context = ""
    for plan in plans:
        result = lookup_refund_policy(plan)
        if result["status"] == "found":
            policy_context += json.dumps(result["results"]) + "\n"

    # Fetch account permissions
    actions = ["refund_processing", "issue_refund_promise", "account_deletion", 
               "password_reset", "plan_upgrade", "plan_downgrade"]
    permissions_context = ""
    for action in actions:
        result = check_account_permissions(action)
        if result["status"] == "found":
            permissions_context += json.dumps(result["results"]) + "\n"

    # Step 2 - Build the prompt for Gemini
    prompt = f"""
    You are a Policy Compliance Agent for a customer support system.

    Your job is to:
    1. Check if the customer query involves any policy sensitive actions
    2. Ensure the response does NOT promise refunds directly
    3. Ensure the response follows the correct refund rules per plan
    4. Assign a confidence score between 0 and 1

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

    # Step 3 - Call Gemini
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    raw = response.text.strip().replace("```json", "").replace("```", "" )

    # Step 4 - Parse and return the result
    raw = response.text.strip().replace("```json", "").replace("```", "")
    result = json.loads(raw)
    result["agent"] = "policy"
    return result