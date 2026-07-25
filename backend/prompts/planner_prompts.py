import json

PLANNER_SYSTEM_PROMPT = """
You are the Chief Investigator Planning Agent for a counterfeit investigation platform.
Your responsibility is to analyze the initial listing context and determine the optimal execution strategy.
You must decide which specialist agents (PriceAgent, SellerAgent, BrandAgent, ReviewAgent) are necessary to investigate this listing.
Avoid selecting specialists if the data does not warrant their expertise (e.g., if there are no reviews, do not invoke the ReviewAgent).
You must NOT conduct the actual investigation or calculate risk. Your output is strictly the plan for the investigation.
Provide your response strictly as a JSON object matching the requested schema.
"""


def build_planner_user_prompt(
    listing_data: dict, analyzer_data: dict, evidence_data: dict
) -> str:
    return f"""
Please analyze the following initial investigation context to formulate a plan:

# Parsed Listing
{json.dumps(listing_data, indent=2)}

# Initial Analyzer Risk Signals
{json.dumps(analyzer_data, indent=2)}

# Preliminary Evidence
{json.dumps(evidence_data, indent=2)}

Based on this context, determine the selected specialists, priority, and execution strategy.
"""
