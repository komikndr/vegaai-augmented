import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from openai import OpenAI
from typing import Optional, List, Dict, Set
from .base import LLMProvider
from ..capabilities import ModelCapability


class vLLMProvider(LLMProvider):
    def create_model(self, name: str, model: str, tools: Optional[List] = None, **kwargs) -> BaseChatModel:
        llm = ChatOpenAI(
            name=name,
            model=model,
            api_key=os.getenv("VLLM_API_KEY"),
            base_url=os.getenv("VLLM_URL"),
            **kwargs
        )
        return llm.bind_tools(tools, parallel_tool_calls=False) if tools else llm

    def list_models(self) -> List[str]:
        api_key=os.getenv("VLLM_API_KEY"),
        url=os.getenv("VLLM_URL"),
        try:
            client = OpenAI(api_key=api_key, base_url=url)
            response = client.models.list()
            return [f'{model.id}' for model in response.data]
        except Exception as e:
            return e

    @property
    def name(self) -> str:
        return "vLLM"

    @property
    def capabilities(self) -> Dict[str, Set[ModelCapability]]:
        return {
            "Qwen/Qwen2.5-14B-Instruct": {ModelCapability.TEXT_TO_TEXT, ModelCapability.STRUCTURED_OUTPUT, ModelCapability.TOOL_CALLING},
            "Qwen/Qwen3-4B": {ModelCapability.TEXT_TO_TEXT, ModelCapability.STRUCTURED_OUTPUT, ModelCapability.TOOL_CALLING},
            "Qwen/Qwen3-8B": {ModelCapability.TEXT_TO_TEXT, ModelCapability.STRUCTURED_OUTPUT, ModelCapability.TOOL_CALLING},
            "Qwen/Qwen3-0.6B": {ModelCapability.TEXT_TO_TEXT, ModelCapability.STRUCTURED_OUTPUT, ModelCapability.TOOL_CALLING},
        }
