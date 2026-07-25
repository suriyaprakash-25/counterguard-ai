from typing import List

from pydantic import BaseModel, Field


class AIInvestigationResult(BaseModel):
    """
    Structured output from the LLM Investigation Agent.
    """

    summary: str = Field(description="A concise summary of the AI's findings.")
    detailed_reasoning: str = Field(
        description="Detailed explanation of why the listing is considered suspicious or safe, referencing specific evidence."
    )
    suspicious_indicators: List[str] = Field(
        description="A list of specific suspicious indicators found by the AI (e.g., 'Inconsistent brand naming', 'Price too low')."
    )
    confidence_score: float = Field(
        description="A confidence score from 0.0 to 100.0 regarding the likelihood of this being a counterfeit or policy violation.",
        ge=0.0,
        le=100.0,
    )
