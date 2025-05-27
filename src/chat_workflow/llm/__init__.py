import os
from typing import List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from .factory import LLMFactory
from .capabilities import ModelCapability  # noqa
from .providers import OpenAIProvider
# from .providers import VLLMProvider

# Initialize factory
llm_factory = LLMFactory()

# Register providers
llm_factory.register_provider("openai", OpenAIProvider())
# llm_factory.register_provider("vllm", VLLMProvider())
