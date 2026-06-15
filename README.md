# Smart-CS Agent

## 基于大语言模型的电商智能客服智能体

> 硕士课程项目 | 2026 年 6 月

---

### 项目简介

一套整合**情绪感知与安抚**、**RAG 知识库检索**和 **Function Calling 工具调度**的电商智能客服原型系统。以 DeepSeek 大语言模型为推理核心，FastAPI 提供后端服务，纯原生前端实现 iMessage 风格聊天界面。

### 核心功能

- **情绪感知**：35+ 负向关键词 + 22+ 正向关键词实时检测，负向情绪自动触发安抚
- **知识库检索**：15 条电商 FAQ，TF-IDF 字符级 n-gram 向量化，Top-K 语义检索
- **工具调用**：物流查询、库存查询、地址修改，完整的 Function Calling 闭环
- **Web 聊天界面**：苹果 iMessage 风格，打字动画，快捷回复
- **CLI 交互**：Rich 终端美化，支持多轮对话

### 项目结构

```
Smart-CS-Agent/
├── main.py                  # CLI 交互入口
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量模板
├── config/
│   └── settings.py          # Pydantic 全局配置
├── agent/
│   ├── prompts.py           # System Prompt 定义
│   ├── emotion.py           # Skill 1: 情绪感知
│   ├── knowledge_base.py    # Skill 2: RAG 检索
│   ├── tools.py             # Skill 3: 工具模块
│   └── agent.py             # 核心编排器
├── api/
│   ├── server.py            # FastAPI 路由
│   └── static/
│       └── index.html       # Web 聊天界面
├── data/
│   ├── knowledge_base.json  # 15 条 FAQ
│   ├── diagrams/            # 系统流程图
│   └── screenshots/         # 界面截图
└── utils/
    └── logger.py
```

### 快速启动

#### 1. 环境要求

- Python 3.9+
- pip

#### 2. 安装依赖

```bash
pip install openai==1.55.0 scikit-learn numpy fastapi uvicorn pydantic pydantic-settings python-dotenv rich
```

#### 3. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 文件，填入:
# OPENAI_API_KEY=你的API-Key
# OPENAI_BASE_URL=https://api.deepseek.com/v1
# LLM_MODEL=deepseek-chat
```

#### 4. 启动 Web 服务

```bash
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
```

#### 5. 打开浏览器

```
http://localhost:8000        # 聊天界面
http://localhost:8000/docs   # API 文档
```

#### CLI 模式

```bash
python main.py
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 大模型 | DeepSeek (deepseek-chat) |
| 后端 | FastAPI + Uvicorn |
| 嵌入 | sklearn TF-IDF |
| 前端 | 原生 HTML/CSS/JS |
| 配置 | Pydantic Settings |
| 终端 | Rich |

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/chat` | 智能对话 |
| POST | `/chat/clear` | 清除历史 |
| GET | `/tools` | 工具列表 |

### 演示截图

![欢迎界面](data/screenshots/01_welcome.png)

![情绪感知](data/screenshots/02_emotion.png)

![物流查询](data/screenshots/03_tool_call.png)

![知识库检索](data/screenshots/04_kb_retrieval.png)

### 系统流程图

架构图、编排器流水线、RAG 检索管线、Function Calling 链路详见 `data/diagrams/` 目录。

### 许可证

仅供课程学习与学术交流使用。
