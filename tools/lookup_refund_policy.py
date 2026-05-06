import json
import os

def lookup_refund_policy(plan_type: str) -> dict:
    """
    MCP Tool: Look up refund policy by plan type.
    Returns refund rules for the given plan type.
    """
    
    # Build the path to the refund_policy.json file
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'refund_policy.json')
    
    # Open and read the file
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    # Search for matching plan type
    results = [policy for policy in data['refund_policies'] if policy['plan_type'] == plan_type]
    
    # Return results
    if results:
        return {"status": "found", "plan_type": plan_type, "results": results}
    else:
        return {"status": "not_found", "plan_type": plan_type, "results": []}