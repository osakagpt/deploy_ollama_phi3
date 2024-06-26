from contextlib import asynccontextmanager
import json
import logging
import os
from typing import AsyncIterable

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx


# info
app_name = "phi3 chatbot"
ollama_url = "http://ollama:11434"
model_name = "finetuned-phi3:latest"
timeout_sec = 600.0

#
# Logger
# ==============================================================================
logger = logging.getLogger("uvicorn")


#
# FastAPI startup and shutdown hook
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # write startup event here
    startup()
    yield
    # write shutdown event here


def startup():
    endpoint = f"{ollama_url}/api/tags"
    try:
        response = httpx.get(endpoint, timeout=timeout_sec)
        if response.status_code == 200:
            models = response.json()["models"]
            if model_name in [model["name"] for model in models]:
                return
        else:
            print("Connection to Ollama server failed.")
            return
    except Exception as ex:
        print(ex)
        return

    endpoint = f"{ollama_url}/api/create"
    json_data = {"name": model_name, "path": "/root/Modelfile"}
    try:
        response = httpx.post(endpoint, json=json_data, timeout=timeout_sec)
        if response.status_code == 200:
            print("Model created successfully.")
        else:
            print("Model creation failed.")
    except Exception as ex:
        print(ex)

    # 空打ちするとモデルがロードされる
    endpoint = f"{ollama_url}/api/chat"
    json_data = {
        "model": model_name,
    }
    try:
        response = httpx.post(endpoint, json=json_data, timeout=timeout_sec)
        if response.status_code == 200:
            print("phi3 model loaded successfully.")
        else:
            print("phi3 model failed to be loaded.")
    except Exception as ex:
        print(ex)

    logger.info("Start chat bot api server.")


def shutdown():
    logger.info("Shutdown chat bot api server.")


#
# FastAPI app instance
# ==============================================================================
app = FastAPI(title=app_name, lifespan=lifespan)
app.mount("/html", StaticFiles(directory="html"), name="html")
# app.mount("/assets", StaticFiles(directory="html/dist/assets"), name="assets")


#
# FastAPI route [GET: http://localhost:8000/]
# ==============================================================================
@app.get("/")
async def root():
    return FileResponse("./html/index.html", media_type="text/html")


#
# FastAPI route [POST: http://localhost:8000/ask]
# ==============================================================================
class PostRequestPayload(BaseModel):
    user_id: int
    user_input: str


@app.post("/")
async def chat(payload: PostRequestPayload) -> StreamingResponse:
    # Infer with prompt without any additional input
    endpoint = f"{ollama_url}/api/chat"
    user_inputs = {"model": "finetuned-phi3", "messages": [{"role": "user", "content": payload.user_input}]}
    return StreamingResponse(event_generator(endpoint, user_inputs), media_type="text/event-stream")


async def event_generator(url: str, data: dict) -> AsyncIterable[str]:
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=data, timeout=60.0) as response:
            async for chunk in response.aiter_bytes():
                ch = json.loads(chunk.decode("utf-8"))
                if ch["done"]:
                    break
                print(ch["message"]["content"])
                yield ch["message"]["content"]
