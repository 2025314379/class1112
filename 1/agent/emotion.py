"""用户情绪感知模块 —— Skill 1"""
import random
from config import settings
from .prompts import EMOTION_ANALYSIS_PROMPT, COMFORT_MESSAGES


class EmotionDetector:
    """情绪检测器：支持关键词匹配 + LLM 分析双模式"""

    # 负向情绪关键词
    NEGATIVE_KEYWORDS = [
        "差评", "投诉", "太慢", "太慢了", "生气", "气死", "垃圾", "骗子",
        "坑爹", "坑人", "退款", "退货", "赔偿", "无语", "失望", "差劲",
        "烂", "火大", "烦", "操", "妈的", "坑", "骗", "假货", "投诉你",
        "什么玩意", "什么鬼", "太差", "我真的服了", "忍无可忍",
    ]

    # 正向情绪关键词
    POSITIVE_KEYWORDS = [
        "谢谢", "感谢", "好评", "不错", "很好", "非常好", "满意", "棒",
        "赞", "喜欢", "开心", "好评", "给力", "nice", "太好了",
        "效率高", "靠谱", "推荐",
    ]

    def __init__(self):
        self._llm_client = None

    @property
    def llm_client(self):
        if self._llm_client is None:
            import httpx
            from openai import OpenAI
            http_client = httpx.Client(verify=False, trust_env=False, timeout=30.0)
            self._llm_client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                http_client=http_client,
            )
        return self._llm_client

    def detect_by_keywords(self, text: str) -> str:
        """基于关键词的快速情绪检测"""
        text_lower = text.lower()
        for kw in self.NEGATIVE_KEYWORDS:
            if kw in text_lower:
                return "negative"
        for kw in self.POSITIVE_KEYWORDS:
            if kw in text_lower:
                return "positive"
        return "neutral"

    def detect_by_llm(self, text: str) -> str:
        """基于 LLM 的情绪分析（更准确）"""
        try:
            response = self.llm_client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "user", "content": EMOTION_ANALYSIS_PROMPT.format(user_message=text)}
                ],
                max_tokens=10,
                temperature=0.0,
            )
            result = response.choices[0].message.content.strip().lower()
            if "negative" in result:
                return "negative"
            elif "positive" in result:
                return "positive"
            return "neutral"
        except Exception:
            return "neutral"

    def analyze(self, text: str, use_llm: bool = False) -> dict:
        """
        综合情绪分析。
        对于明显的负向关键词，直接返回结果（更快）；
        对于复杂情况，可选启用 LLM 分析。
        """
        # 先用关键词快速检测
        emotion = self.detect_by_keywords(text)

        # 如果关键词检测为中性且启用 LLM，用 LLM 二次分析
        if emotion == "neutral" and use_llm:
            emotion = self.detect_by_llm(text)

        comfort_msg = ""
        if emotion == "negative":
            comfort_msg = random.choice(COMFORT_MESSAGES["negative"])

        return {
            "emotion": emotion,
            "comfort_message": comfort_msg,
            "need_human_support": emotion == "negative",
        }
