import asyncio
import logging
from typing import Dict, Any, List
from openai import OpenAI, AsyncOpenAI
from config import Config

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(
        self,
        provider: str = "openai",
        api_key: str = None,
        model: str = None,
        temperature: float = Config.TEMPERATURE,
        tokens_per_round: int = None
    ):
        self.provider = provider.lower()
        self.temperature = temperature
        self.tokens_per_round = tokens_per_round

        if self.provider == "openai":
            self.api_key = api_key or Config.OPENAI_API_KEY
            self.model = model or Config.GPT_MODEL
            self.client = OpenAI(api_key=self.api_key)
            self.a_client = AsyncOpenAI(api_key=self.api_key)

        elif self.provider == "openrouter":
            self.api_key = api_key or Config.OPEN_ROUTER_API_KEY
            self.model = model or Config.OPEN_ROUTER_MODEL
            base_url = "https://openrouter.ai/api/v1"
            self.client = OpenAI(api_key=self.api_key, base_url=base_url)
            self.a_client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)

        else:
            raise ValueError("Unsupported provider. Use 'openai' or 'openrouter'.")

    def _supports_temperature(self) -> bool:
        # Only include temperature for models whose name contains "gpt"
        return "gpt" in self.model.lower()


    async def a_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = None,
        max_tokens: int = None,
        timeout: float = 60
    ) -> str:
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stop":None,
            "response_format": {"type": "json_object"}

        }
        temp = temperature if temperature is not None else self.temperature
        if self._supports_temperature() and temp is not None:
            params["temperature"] = temp

        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        elif self.tokens_per_round is not None:
            params["max_tokens"] = self.tokens_per_round

        try:
            response = await self.a_client.chat.completions.create(**params)
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            logger.error(f"API call timed out after {timeout} seconds")
            raise
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise
