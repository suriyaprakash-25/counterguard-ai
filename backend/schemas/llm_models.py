from typing import List

from pydantic import BaseModel, Field


class AIInvestigationResult(BaseModel):
    """
    Structured output from the LLM Investigation Agent (Coordinator).
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


class PlanningResult(BaseModel):
    """
    Structured output from the LLM Planning Agent.
    """

    selected_specialists: List[str] = Field(
        description="List of specialist agents to execute (e.g., 'PriceAgent', 'SellerAgent', 'BrandAgent', 'ReviewAgent')."
    )
    priority: str = Field(description="Investigation priority (High, Medium, Low).")
    execution_strategy: str = Field(
        description="Description of how the investigation should proceed based on the initial context."
    )
    rationale: str = Field(description="Reasoning behind the chosen plan.")


class PriceAnalysisResult(BaseModel):
    anomaly_detected: bool = Field(
        description="True if pricing anomalies are detected."
    )
    reasoning: str = Field(description="Explanation of the pricing evaluation.")
    risk_score: int = Field(description="Risk score from 0 to 100.", ge=0, le=100)


class SellerAnalysisResult(BaseModel):
    reputation_risk: str = Field(description="High, Medium, or Low reputation risk.")
    reasoning: str = Field(description="Explanation of the seller evaluation.")
    risk_score: int = Field(description="Risk score from 0 to 100.", ge=0, le=100)


class BrandAnalysisResult(BaseModel):
    authenticity_flags: List[str] = Field(
        description="List of brand inconsistency flags."
    )
    reasoning: str = Field(description="Explanation of the brand evaluation.")
    risk_score: int = Field(description="Risk score from 0 to 100.", ge=0, le=100)


class ReviewAnalysisResult(BaseModel):
    fake_reviews_detected: bool = Field(
        description="True if review patterns seem fake."
    )
    reasoning: str = Field(description="Explanation of the reviews evaluation.")
    risk_score: int = Field(description="Risk score from 0 to 100.", ge=0, le=100)
