import httpx
from loguru import logger

from config import settings


class OpenRouterClient:
    def __init__(self, base_url: str = "https://openrouter.ai/api"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        }

    async def send_request(self, prompt: str, max_tokens: int = 100):
        logger.info("Waiting resulf from LLM...")
        endpoint = f"{self.base_url}/v1/completions"
        payload = {
            "model": settings.MODEL_LLM,
            "prompt": prompt,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=payload, headers=self.headers)
        response.raise_for_status()
        logger.info("Got result from LLM...")
        return response.json()["choices"][0]["text"]