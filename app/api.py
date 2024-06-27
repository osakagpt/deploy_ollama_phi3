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
model_name = "osakagpt/finetuned-phi3:latest"
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
    pull_model(model_name)
    if is_available(model_name):
        load_model(model_name)
        logger.info("Start chat bot api server.")


def shutdown():
    logger.info("Shutdown chat bot api server.")


def create_model(name):
    # create model, ggufをサーバーに置いておく必要あり
    endpoint = f"{ollama_url}/api/create"
    json_data = {"name": name, "path": "/root/Modelfile"}
    try:
        response = httpx.post(endpoint, json=json_data, timeout=timeout_sec)
        if response.status_code == 200:
            print("Model created successfully.")
        else:
            print("Model creation failed.")
    except Exception as ex:
        print(ex)


def push_model(name):
    # push
    endpoint = f"{ollama_url}/api/push"
    json_data = {"model": name, "insecure": True}
    try:
        response = httpx.post(endpoint, json=json_data, timeout=timeout_sec)
        if response.status_code == 200:
            print("Model pushed successfully.")
        else:
            print("Model push failed.")
    except Exception as ex:
        print(ex)


def pull_model(name):
    endpoint = f"{ollama_url}/api/pull"
    json_data = {"model": name}
    try:
        response = httpx.post(endpoint, json=json_data, timeout=timeout_sec)
        if response.status_code == 200:
            print("Model pulled successfully.")
        else:
            print("Model pull failed.")
    except Exception as ex:
        print(ex)


def is_available(name):
    # そのモデルが使えるかどうか
    endpoint = f"{ollama_url}/api/tags"
    try:
        response = httpx.get(endpoint, timeout=timeout_sec)
        if response.status_code == 200:
            models = response.json()["models"]
            if name in [model["name"] for model in models]:
                return True
            else:
                return False
        else:
            print("Connection to Ollama server failed.")
            return False
    except Exception as ex:
        print(ex)
        return False


def load_model(name):
    # 空打ちするとモデルがロードされる
    endpoint = f"{ollama_url}/api/chat"
    json_data = {"model": name}
    try:
        response = httpx.post(endpoint, json=json_data, timeout=timeout_sec)
        if response.status_code == 200:
            print("phi3 model loaded successfully.")
        else:
            print("phi3 model failed to be loaded.")
    except Exception as ex:
        print(ex)


#
# FastAPI app instance
# ==============================================================================
app = FastAPI(title=app_name, lifespan=lifespan)
app.mount("/html", StaticFiles(directory="html"), name="html")


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
    user_inputs = {"model": model_name, "messages": [{"role": "user", "content": payload.user_input}]}
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
