
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from config import settings
from rabbit_sender import RabbitMQClient

app = FastAPI()

class WebhookRequest(BaseModel):
    message: str
    callback_url: HttpUrl


limiter = Limiter(key_func=get_remote_address)


history = {}

rabbitmq_client = RabbitMQClient()

@app.on_event("startup")
async def startup_event():
    logger.info("Connecting to rabbitmq")
    await rabbitmq_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Disconnecting from rabbitmq")
    await rabbitmq_client.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    errors = exc.errors()
    custom_errors = [
        {
            "error": error["msg"],
        }
        for error in errors
    ]
    logger.debug(f"Validation details: {custom_errors}")

    return JSONResponse(
        status_code=400,
        content={"detail": custom_errors},
    )


@app.post("/webhook")
@limiter.limit("10/minute")
async def handle_webhook(wb_request: WebhookRequest,request: Request):
    try:
        logger.info("New request received")
        logger.info(f"Sending to RabbitMQ: {wb_request.message}")
        request_dict = wb_request.__dict__
        request_dict['callback_url'] = str(request_dict['callback_url'])
        request_dict['ip'] = request.client.host
        await rabbitmq_client.publish_message(settings.QUEUE_NAME, request_dict)
        return {"status": "success", "response": "OK"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/callback")
async def receive_result(request: Request):
    return {"status": "success"}

"""
curl -X POST "http://127.0.0.1:8000/webhook" \
-H "Content-Type: application/json" \
-d '{
    "message": "kazakhstan capital",
    "callback_url": "http://127.0.0.1:8000/callback"
}'

"""