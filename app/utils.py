import httpx
from loguru import logger

from config import settings


async def send_telegram_msg(response:str):
    async with httpx.AsyncClient() as client:
        url = f'https://api.telegram.org/bot{settings.TG_BOT}/sendMessage'
        payload = {
            'chat_id': settings.CHAT_ID,
            'text': response
        }
        res = await client.post(url, json=payload)
        return res.status_code


async def send_callback(url, status_code):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.info("URL is reachable")
            logger.info(status_code)
            headers = {"Content-Type": "application/json"}
            r= await client.post(url, headers=headers,json={"status_code": status_code})
            print(r.json())
    except httpx.RequestError as e:
        print(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}")