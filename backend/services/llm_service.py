import logging

from openai import OpenAI

from backend.exceptions import CounterGuardError
from backend.schemas.llm_models import AIInvestigationResult
from backend.settings import settings

logger = logging.getLogger(__name__)


class LLMServiceError(CounterGuardError):
    """Raised when the LLM service fails to generate a valid response."""

    pass


class LLMService:
    def __init__(self, model_name: str = "gpt-4o-mini", timeout: int = 30):
        self.model_name = model_name
        self.timeout = timeout
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            # We will default to a dummy client if no key is provided during testing,
            # but ideally we should raise an error. For robust testing without key, we mock it.
            logger.warning(
                "OPENAI_API_KEY is not set. LLMService may fail unless mocked."
            )
            self.client = OpenAI(api_key="dummy")
        else:
            self.client = OpenAI(api_key=api_key)

    def generate_investigation_result(
        self, system_prompt: str, user_prompt: str
    ) -> AIInvestigationResult:
        """
        Calls the LLM and forces a structured JSON output mapped to AIInvestigationResult.
        """
        logger.info(f"Querying LLM ({self.model_name}) for investigation reasoning.")
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=AIInvestigationResult,
                timeout=self.timeout,
            )

            result = response.choices[0].message.parsed
            if not result:
                raise LLMServiceError("LLM returned an empty parsed result.")

            logger.info("Successfully received structured response from LLM.")
            return result

        except Exception as e:
            logger.error(f"LLM Service failed: {e}")
            raise LLMServiceError(f"Failed to generate AI investigation result: {e}")
