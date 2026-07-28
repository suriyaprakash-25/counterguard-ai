import logging
import traceback
from typing import Optional

from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError

from backend.exceptions import CounterGuardError
from backend.settings import settings

logger = logging.getLogger(__name__)


class LLMServiceError(CounterGuardError):
    """Raised when the LLM service fails to generate a valid response."""

    pass


class LLMService:
    def __init__(self, model_name: Optional[str] = None, timeout: int = 30):
        self.timeout = timeout
        self.is_groq = False

        if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
            logger.info("Initializing LLMService with Groq API Key (Llama 3.3 70B).")
            self.is_groq = True
            self.model_name = model_name or "llama-3.3-70b-versatile"
            self.client = OpenAI(
                api_key=settings.GROQ_API_KEY.strip(),
                base_url="https://api.groq.com/openai/v1",
            )
        elif settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            logger.info("Initializing LLMService with Gemini API Key.")
            self.model_name = model_name or "gemini-2.0-flash"
            self.client = OpenAI(
                api_key=settings.GEMINI_API_KEY.strip(),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
        elif settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            logger.info("Initializing LLMService with OpenAI API Key.")
            self.model_name = model_name or "gpt-4o-mini"
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY.strip())
        else:
            logger.warning(
                "No valid LLM API key set in settings/env. LLMService will use fallback mode."
            )
            self.model_name = model_name or "gpt-4o-mini"
            self.client = OpenAI(api_key="dummy")

    def generate_structured_response(
        self, system_prompt: str, user_prompt: str, response_model: type
    ):
        """
        Calls the LLM and forces a structured JSON output mapped to the given Pydantic model.
        """
        logger.info(
            f"[LLMService] Querying {self.model_name} for {response_model.__name__}"
        )
        try:
            if self.is_groq:
                # Groq uses json_object mode with Pydantic JSON schema in system prompt
                schema = response_model.model_json_schema()
                enhanced_sys_prompt = (
                    f"{system_prompt}\n\n"
                    f"CRITICAL REQUIREMENT: You MUST respond ONLY with valid JSON matching this exact JSON schema: {schema}"
                )
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": enhanced_sys_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    timeout=self.timeout,
                )

                raw_content = response.choices[0].message.content
                if not raw_content:
                    raise LLMServiceError("Groq returned empty completion content.")

                result = response_model.model_validate_json(raw_content)
            else:
                # OpenAI / Gemini native parsing
                response = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=response_model,
                    timeout=self.timeout,
                )

                result = response.choices[0].message.parsed
                if not result:
                    raise LLMServiceError("LLM returned an empty parsed result.")

            logger.info("[LLMService] Successfully received structured response from LLM.")
            return result

        except RateLimitError as e:
            logger.error(
                f"[LLMService] HTTP 429 Quota Exceeded / Rate Limit on {self.model_name}: {e.message}"
            )
            logger.debug(traceback.format_exc())
            raise LLMServiceError(f"HTTP 429 RateLimit/Quota Exceeded: {e.message}") from e
        except AuthenticationError as e:
            logger.error(
                f"[LLMService] HTTP 401 Authentication Failure on {self.model_name}: {e.message}"
            )
            logger.debug(traceback.format_exc())
            raise LLMServiceError(f"HTTP 401 Auth Failure: {e.message}") from e
        except APIConnectionError as e:
            logger.error(f"[LLMService] Network/Connection error reaching {self.model_name}: {e.message}")
            logger.debug(traceback.format_exc())
            raise LLMServiceError(f"Connection error: {e.message}") from e
        except APIError as e:
            logger.error(
                f"[LLMService] API Error ({getattr(e, 'status_code', 'unknown')}) on {self.model_name}: {e.message}"
            )
            logger.debug(traceback.format_exc())
            raise LLMServiceError(f"API Error {getattr(e, 'status_code', '')}: {e.message}") from e
        except Exception as e:
            logger.error(f"[LLMService] Unexpected error querying {self.model_name}: {e}")
            logger.debug(traceback.format_exc())
            raise LLMServiceError(f"Unexpected error: {e}") from e
