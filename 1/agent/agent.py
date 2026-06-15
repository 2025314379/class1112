"""智能客服 Agent 核心编排模块
整合情绪感知、知识库检索、工具调用三大技能。
"""
import json
from typing import Optional, List, Dict, Any
from config import settings
from .prompts import SYSTEM_PROMPT
from .emotion import EmotionDetector
from .knowledge_base import KnowledgeBase
from .tools import TOOLS_DEFINITION, TOOL_FUNCTIONS

# 延迟导入 OpenAI（避免未安装时整个模块不可用）
_OpenAI = None


def _get_openai():
    global _OpenAI
    if _OpenAI is None:
        from openai import OpenAI as _OpenAI
    return _OpenAI


class SmartCSAgent:
    """全能型电商智能客服助手"""

    def __init__(self):
        self._llm_client = None
        self.emotion_detector = EmotionDetector()
        self.knowledge_base = KnowledgeBase()
        self.conversation_history: list[dict] = []

    @property
    def llm_client(self):
        if self._llm_client is None:
            import httpx
            OpenAI = _get_openai()
            http_client = httpx.Client(verify=False, trust_env=False, timeout=60.0)
            self._llm_client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                http_client=http_client,
            )
        return self._llm_client

    def _build_messages(self, user_message: str, kb_context: str, emotion_info: dict) -> list[dict]:
        """构建发送给 LLM 的完整消息列表"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # 注入历史对话（最近 6 轮）
        for msg in self.conversation_history[-12:]:
            messages.append(msg)

        # 构建增强后的用户消息
        enhanced_message = user_message

        # 注入知识库上下文
        if kb_context:
            enhanced_message = f"{kb_context}\n\n---\n用户问题：{user_message}"

        # 如果检测到负向情绪，在消息前加入安抚提示
        if emotion_info["emotion"] == "negative":
            enhanced_message = (
                f"[系统提示：用户情绪为负向/愤怒，请先进行情感安抚，"
                f"然后优先处理用户诉求。]\n\n{enhanced_message}"
            )

        messages.append({"role": "user", "content": enhanced_message})
        return messages

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """执行工具调用并返回结果"""
        func = TOOL_FUNCTIONS.get(tool_name)
        if func is None:
            return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
        try:
            result = func(**arguments)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def chat(self, user_message: str) -> dict:
        """
        处理用户消息的主流程：
        1. 情绪感知
        2. 知识库检索
        3. LLM 推理（含工具调用）
        """
        # Step 1: 情绪分析
        emotion_info = self.emotion_detector.analyze(user_message)

        # Step 2: 知识库检索
        kb_results = self.knowledge_base.search(user_message, top_k=3)
        kb_context = self.knowledge_base.format_context(kb_results)

        # Step 3: 构建消息并调用 LLM
        messages = self._build_messages(user_message, kb_context, emotion_info)

        # 调用 LLM（支持 Function Calling）
        try:
            response = self.llm_client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                tools=TOOLS_DEFINITION,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=800,
            )
        except Exception as e:
            return {
                "reply": f"抱歉，系统暂时遇到了一些问题（{str(e)[:100]}），请稍后再试或联系人工客服。",
                "emotion": emotion_info,
                "kb_used": [],
                "tool_calls": None,
            }

        choice = response.choices[0]
        assistant_message = choice.message

        # 处理工具调用
        tool_results = None
        if assistant_message.tool_calls:
            tool_results = []
            # 先添加 assistant 消息（含 tool_calls）
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ],
            })

            for tc in assistant_message.tool_calls:
                func_name = tc.function.name
                arguments = json.loads(tc.function.arguments)
                result = self._execute_tool(func_name, arguments)

                tool_results.append({
                    "tool_name": func_name,
                    "arguments": arguments,
                    "result": json.loads(result) if isinstance(result, str) else result,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

            # 用工具结果再次调用 LLM 生成最终回复
            try:
                final_response = self.llm_client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800,
                )
                assistant_reply = final_response.choices[0].message.content
            except Exception:
                assistant_reply = assistant_message.content or "已为您处理，请查看结果。"

        else:
            assistant_reply = assistant_message.content

        # 保存对话历史
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_reply})
        # 限制历史长度
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        return {
            "reply": assistant_reply,
            "emotion": emotion_info,
            "kb_used": [r["question"] for r in kb_results if r["score"] >= 0.3],
            "tool_calls": tool_results,
        }

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []
