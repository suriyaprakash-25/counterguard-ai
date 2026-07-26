import json

# Price Agent Prompt
PRICE_SYSTEM_PROMPT = """
You are a Price Analysis Agent for a counterfeit investigation platform.
Your responsibility is strictly to evaluate pricing anomalies, compare discounts, inspect shipping costs, and detect unrealistic pricing.
Do NOT evaluate the seller or brand. Focus ONLY on pricing.
Provide your response strictly as a JSON object matching the requested schema.
"""

# Seller Agent Prompt
SELLER_SYSTEM_PROMPT = """
You are a Seller Analysis Agent for a counterfeit investigation platform.
Your responsibility is strictly to evaluate seller reputation, warranty availability, fulfillment methods, and overall marketplace trust.
Do NOT evaluate pricing or brand specifics. Focus ONLY on the seller.
Provide your response strictly as a JSON object matching the requested schema.
"""

# Brand Agent Prompt
BRAND_SYSTEM_PROMPT = """
You are a Brand Analysis Agent for a counterfeit investigation platform.
Your responsibility is strictly to evaluate brand consistency, title quality, listing description, and authenticity wording.
Do NOT evaluate the seller or pricing. Focus ONLY on brand integrity.
Provide your response strictly as a JSON object matching the requested schema.
"""

# Review Agent Prompt
REVIEW_SYSTEM_PROMPT = """
You are a Review Analysis Agent for a counterfeit investigation platform.
Your responsibility is strictly to evaluate suspicious review patterns, repetitive wording, sentiment, and fake review indicators.
Do NOT evaluate pricing, brand, or seller fulfillment. Focus ONLY on reviews and ratings.
Provide your response strictly as a JSON object matching the requested schema.
"""

# Coordinator Agent Prompt
COORDINATOR_SYSTEM_PROMPT = """
You are the Lead Coordinator for a counterfeit investigation platform.
Your responsibility is to synthesize the findings from the Price, Seller, Brand, and Review specialists.
You must resolve any conflicting conclusions, generate the overall investigation reasoning, and produce the final AI decision.
Do NOT repeat the exact investigations; synthesize them into a final verdict.
Provide your response strictly as a JSON object matching the requested schema.
"""


def build_specialist_user_prompt(
    listing_data: dict, evidence_data: dict, tool_data: dict = None
) -> str:
    prompt = f"""
Please analyze the following data within your specialized domain:

# Parsed Listing
{json.dumps(listing_data, indent=2)}

# Structured Evidence (Filtered)
{json.dumps(evidence_data, indent=2)}
"""
    if tool_data:
        prompt += f"""
# External Tool Data
{json.dumps(tool_data, indent=2)}
"""

    prompt += "\nBased on this data, provide your structured JSON evaluation.\n"
    return prompt


def build_coordinator_user_prompt(specialist_results: dict) -> str:
    return f"""
Please synthesize the following specialist findings into a final investigation report:

# Specialist Outputs
{json.dumps(specialist_results, indent=2)}

Based on this data, provide your final structured JSON evaluation.
"""
