# Embedding 接入说明

本文档用于说明项目中大模型 [`Embedding`](docs/resource/llm-account/embedding-function.md:1) 的接入方式。

## 目标

- 在需要向量化能力时，优先使用 **大模型 API** 提供的 embedding 能力
- 不使用本地 [`sentence_transformers`](docs/resource/llm-account/embedding-function.md:8) 模型方案

## 推荐方式

当前推荐使用火山引擎 Ark Runtime 提供的 embedding 接口，通过 API 调用获取文本向量。

## 依赖安装

```bash
pip install --upgrade "volcengine-python-sdk[ark]"
```

## Python 接入示例

### 1. 初始化客户端

```python
import os

from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

load_dotenv()

client = Ark(api_key=os.getenv("ARK_API_KEY"))
model_name = os.getenv("ARK_EMBEDDING_MODEL", "doubao-embedding-vision-251215")
```

### 2. 单文本 Embedding

```python
def get_text_embedding(text: str) -> list[float]:
    response = client.multimodal_embeddings.create(
        model=model_name,
        input=[
            {
                "type": "text",
                "text": text,
            }
        ],
    )
    return response.data.embedding
```

### 3. 批量文本 Embedding

```python
def get_batch_embeddings(texts: list[str]):
    inputs = [
        {
            "type": "text",
            "text": text,
        }
        for text in texts
    ]

    response = client.multimodal_embeddings.create(
        model=model_name,
        input=inputs,
    )
    return response.data
```
