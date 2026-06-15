"""FastAPI 服务 —— 为智能客服 Agent 提供 RESTful API"""
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import SmartCSAgent
from config import settings

app = FastAPI(
    title="Smart-CS Agent API",
    description="全能型电商智能客服助手 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

agent = SmartCSAgent()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    clear_history: bool = Field(default=False)


class ChatResponse(BaseModel):
    reply: str
    emotion: Dict[str, Any] = Field(default_factory=dict)
    kb_used: List[str] = Field(default_factory=list)
    tool_calls: Optional[list] = Field(default=None)


@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Smart-CS Agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if request.clear_history:
            agent.clear_history()
        result = agent.chat(request.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/clear")
async def clear_chat():
    agent.clear_history()
    return {"message": "对话历史已清除"}


@app.get("/tools")
async def list_tools():
    from agent.tools import TOOLS_DEFINITION
    tools_info = []
    for t in TOOLS_DEFINITION:
        func = t["function"]
        tools_info.append({"name": func["name"], "description": func["description"]})
    return {"tools": tools_info}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
