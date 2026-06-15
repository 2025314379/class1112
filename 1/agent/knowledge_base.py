"""知识库检索模块 (RAG) —— Skill 2
使用 TF-IDF + 余弦相似度进行本地知识库检索，无外部依赖。
支持自动回退到 sentence-transformers / ONNX 作为增强嵌入方案。
"""
import json
import os
import numpy as np
from config import settings


class KnowledgeBase:
    """电商知识库：基于 TF-IDF 的 FAQ 检索"""

    def __init__(self):
        self.data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base.json"
        )
        self.qa_pairs: list[dict] = []
        self.documents: list[str] = []
        self.vectorizer = None
        self.doc_vectors = None
        self._use_sentence_transformers = False
        self._st_model = None
        self._load_data()
        self._build_index()

    def _load_data(self):
        """从 JSON 加载知识库"""
        if not os.path.exists(self.data_path):
            print(f"[KnowledgeBase] 数据文件不存在: {self.data_path}")
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            self.qa_pairs = json.load(f)

        self.documents = [
            f"Q: {qa['question']}\nA: {qa['answer']}"
            for qa in self.qa_pairs
        ]
        print(f"[KnowledgeBase] 已加载 {len(self.qa_pairs)} 条知识")

    def _build_index(self):
        """构建向量索引"""
        # 尝试 sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(settings.embedding_model)
            self._st_model.encode(["test"])
            self.doc_vectors = self._st_model.encode(self.documents)
            self._use_sentence_transformers = True
            print(f"[KnowledgeBase] 使用 sentence-transformers: {settings.embedding_model}")
            return
        except Exception as e:
            print(f"[KnowledgeBase] sentence-transformers 不可用: {e}")

        # 回退到 TF-IDF（使用字符级 n-gram 支持中文）
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(1, 3),
            max_features=1024,
        )
        self.doc_vectors = self.vectorizer.fit_transform(self.documents)
        self._cosine_similarity = cosine_similarity
        print("[KnowledgeBase] 使用 sklearn TF-IDF (char n-gram) 向量化")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """检索与查询最相关的知识条目"""
        if not self.qa_pairs:
            return []

        try:
            if self._use_sentence_transformers and self._st_model:
                query_vec = self._st_model.encode([query])
                similarities = np.dot(self.doc_vectors, query_vec.T).flatten()
                # 归一化
                doc_norms = np.linalg.norm(self.doc_vectors, axis=1)
                query_norm = np.linalg.norm(query_vec)
                similarities = similarities / (doc_norms * query_norm + 1e-10)
            else:
                query_vec = self.vectorizer.transform([query])
                similarities = self._cosine_similarity(self.doc_vectors, query_vec).flatten()

            # 取 top_k
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score < 0.05:
                    continue
                results.append({
                    "question": self.qa_pairs[idx]["question"],
                    "answer": self.qa_pairs[idx]["answer"],
                    "score": score,
                })
            return results
        except Exception as e:
            print(f"[KnowledgeBase] 检索失败: {e}")
            return []

    def format_context(self, results: list[dict], threshold: float = 0.1) -> str:
        """将检索结果格式化为 LLM 上下文"""
        if not results:
            return ""

        filtered = [r for r in results if r["score"] >= threshold]
        if not filtered:
            return ""

        lines = ["以下是知识库中与用户问题相关的信息："]
        for i, item in enumerate(filtered[:3], 1):
            lines.append(f"{i}. Q: {item['question']}")
            lines.append(f"   A: {item['answer']}")
        return "\n".join(lines)
