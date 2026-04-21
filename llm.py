import os
from langchain_anthropic import ChatAnthropic

# Default to Claude Sonnet 4 for balance of capability and cost
DEFAULT_MODEL = "MiniMax-M2.7"


# def get_llm(model: str = DEFAULT_MODEL) -> ChatAnthropic:
#     """Create and return an Anthropic LLM instance.
#
#     Args:
#         model: Anthropic model name. Defaults to "MiniMax-M2.7".
#
#     Returns:
#         ChatAnthropic instance configured with environment API key.
#
#     Environment:
#         ANTHROPIC_API_KEY: Required for authentication with Anthropic API.
#     """
#     api_key = os.environ.get("ANTHROPIC_API_KEY")
#     if not api_key:
#         raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
#
#     return ChatAnthropic(model=model, api_key=api_key)
from langchain_deepseek import ChatDeepSeek
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 中的 DEEPSEEK_API_KEY

# 初始化 DeepSeek 模型
def get_llm():
    llm = ChatDeepSeek(
        model="deepseek-chat",          # 或 "deepseek-reasoner" 如果用推理模型
        max_tokens=8192,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
    )
    return llm

