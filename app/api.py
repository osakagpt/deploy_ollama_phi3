from base64 import b64decode
import logging
import os
import json
from typing import Iterable, List, TypedDict

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from starlette.middleware.cors import CORSMiddleware

#
# Logger
# ==============================================================================
logger = logging.getLogger("uvicorn")


#
# FastAPI app instance
# ==============================================================================
app = FastAPI()
app.mount("/html", StaticFiles(directory="html"), name="html")
# app.mount("/assets", StaticFiles(directory="html/dist/assets"), name="assets")


#
# FastAPI startup hook
# ==============================================================================
@app.on_event("startup")
async def startup():
    logger.info("Start chat bot api server.")


#
# FastAPI shutdown hook
# ==============================================================================
@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutdown chat bot api server.")


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
async def ask(payload: PostRequestPayload):
    # Infer with prompt without any additional input
    url = "http://ollama:11434/api/generate"
    user_inputs = {
        "model": "phi3",
        "prompt": payload.user_input,
    }
    output = ""
    try:
        response = requests.post(url, data=json.dumps(user_inputs))
        if response.ok:
            resp_list = response.text.split("\n")[:-1]
            for resp in resp_list:
                j = json.loads(resp)
                output += j["response"]
        else:
            output += "ごめんよくわからかった.もう一回言って"
    except Exception as ex:
        print(ex)
        output += "接続できてないよ"
    return {"output": output}
